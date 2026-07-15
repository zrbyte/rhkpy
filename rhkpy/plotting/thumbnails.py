"""Thumbnail (png) generation for sm4 files, using a headless browser for
the Bokeh/Panel png export.

Moved verbatim from rhkpy_process.py (refactor phase 2).
"""

import glob
import os

import panel as pn


def _setup_webdriver():
	"""Create a headless Selenium WebDriver for Bokeh/Panel png export.

	Tries Chrome, then Edge, then Firefox. The matching driver binary is provisioned
	automatically by Selenium Manager (bundled with ``selenium`` >= 4.6), so no manual
	driver download or ``PATH`` setup is needed on Windows or macOS. Only a supported
	browser needs to be installed (Edge ships with Windows, Chrome is common on macOS).

	:return: a headless WebDriver instance, or None if selenium is missing or no
		supported browser could be started.
	"""
	try:
		from selenium import webdriver
	except ImportError:
		print('Selenium is not installed. Install it with "pip install selenium" to enable png export.')
		return None

	def _chrome():
		from selenium.webdriver.chrome.options import Options
		opts = Options()
		opts.add_argument('--headless=new')
		return webdriver.Chrome(options = opts)

	def _edge():
		from selenium.webdriver.edge.options import Options
		opts = Options()
		opts.add_argument('--headless=new')
		return webdriver.Edge(options = opts)

	def _firefox():
		from selenium.webdriver.firefox.options import Options
		opts = Options()
		opts.add_argument('--headless')
		return webdriver.Firefox(options = opts)

	# try each browser in turn; Selenium Manager fetches the matching driver
	for browser, factory in [('Chrome', _chrome), ('Edge', _edge), ('Firefox', _firefox)]:
		try:
			return factory()
		except Exception:
			continue

	print('Could not start a headless browser (tried Chrome, Edge and Firefox) for png export.'
		'\n\tInstall one of these browsers, then rerun genthumbs.')
	return None

def genthumbs(folderpath = './', **kwargs):
	"""Generate thumbnails for the sm4 files present in the current folder (usually the folder where the jupyter notebook is present).
	It ``folderpath`` is specified it generates the thumbnails in the path given.
	All other files are ignored. Subfolders are ignored.
	The method uses :func:`~rhkpy.rhkpy_loader.rhkdata.qplot` to make the png images.

	:param folderpath: path to the folder containing the sm4 files, defaults to './'
	:type folderpath: str, optional

	:Example:
		
		.. code-block:: python

			import rhkpy

			# generate thumbnails of the sm4 files in the current working directory
			rhkpy.genthumbs()

			# generate thumbnails for the folder "stm measurements/maps"
			rhkpy.genthumbs(folderpath = './stm measurements/maps/')

	.. note::

		Possible options for ``folderpath`` are:
		
		- relative path: "./" means the current directory. "../" is one directory above the current one.
		- absolute path: Can start with: "c:/users/averagejoe/data"

		If you use backslashes to separate folder names, remember to append "r" to the beginning of the path to escape backslashes. For example: ``folderpath = r"c:\\users\\averagejoe\\data"``.
		Paths can be copied directly from Windows explorer, if you append an "r".

	.. note::

		Exporting png images uses the Bokeh png export, which requires a headless browser.
		:func:`genthumbs` starts one automatically (trying Chrome, Edge, then Firefox in this order) and the matching driver is downloaded by Selenium Manager, so no manual driver setup is needed.
		One of these browsers needs to be installed on the machine.
		Files that fail to load, plot or save are skipped with a printed message; the rest of the batch is still processed.
	"""
	# import some dependencies (lazy, to avoid a circular import with rhkpy.core)
	from ..core import rhkdata
	from ..builders.detect import _get_filename

	# get the sm4 filenames in the folder
	sm4list = glob.glob(os.path.join(folderpath, '*.sm4'))
	filenames = []
	for sm4path in sm4list:
		filenames += [_get_filename(sm4path)]

	if not filenames:
		print('No .sm4 files found in:', folderpath)
		return

	# Set up a single headless browser for Bokeh/Panel png export and reuse it for
	# every file. Panel uses ``pn.state.webdriver`` if it is set and only spins up its
	# own (PATH-based) driver otherwise, so providing one here avoids the manual driver
	# install and works the same on Windows and macOS.
	previous_webdriver = pn.state.webdriver
	driver = _setup_webdriver()
	if driver is None:
		return
	pn.state.webdriver = driver

	try:
		# generate thumbs
		for fname in filenames:
			# load the file, plot the thumbnail and save it; skip to the next
			# file if any of these steps fails, so one bad file does not abort the batch
			try:
				data = rhkdata(os.path.join(folderpath, fname))
				data_plot = data.qplot()
				data_plot.save(os.path.join(folderpath, fname[:-4] + '.png'))
			except Exception as e:
				# handle the exception
				print('An error occured in file:', fname, '\n\tThe error is:', e)
				continue
	finally:
		# shut down the browser and restore any previously configured webdriver
		driver.quit()
		pn.state.webdriver = previous_webdriver
