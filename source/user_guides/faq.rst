FAQs
****

ROIs
====
	#. Can I delete an ROI?
		- See ROI Manager guide. <link here>

	#. I don’t want to delete ROIs but I want to mark them for exclusion in further analysis, how can I do this?
		- You can do this by creating an ROI type category. See <link here> *Add New ROI Type Later* which uses this as an example. You can also create this ROI Type category when you create a New Project, not necessarily when you already have a project as the example uses.

	#. Can I tag more than one piece of information to each ROI?
		- Yes, add as many ROI Type categories as you want in the Project Configuration.

		.. seealso:: :ref:`Project Configuration <project-configuration>` <tagging_rois_link>

	#. I already have a Mesmerize project with many Samples in it. Can I add a new ROI Type category?
		- Yes see <link here> *Add New ROI Type Later guide*

	#. Can some samples in my project have ROIs that originate from CNMF(E) and others that are manually drawn?
		- This is not recommended.

CNMFE
=====
	#. I have ROIs that clearly encompass multiple cells instead of just one
		- Increase min_coor, see <link here> *CNMFE guide*.
		- Might help to reduce gSig as well

	#. I have too many garbage ROIs around random regions that are clearly noise
		- Increase <link here> *min_pnr*

	#. Min_PNR image is completely blue and void of any signals
		- Increase <link here> *gSig*

	#. Vmin slider is stuck in Inspect Correlation & PNR GUI.
		-  Close and reopen it. This is a matplotlib issue, not something I can fix.

Caiman Motion Correction
========================

	#. I have video tearing
		- Try increasing *upsample grid* <link here>
		- It’s possible that the movement is too severe to be motion corrected. When the movement is so severe that the information does not exist, it is impossible to motion correct it.

	#. My animal is growing
		- This is growth, not motion. Unfortunately cannot be corrected for. If you have an idea for a technique I can try it out.

	#. The output actually has more motion, it has created false motion.
		- Try these things:
			- Reduce *Strides* & *Overlaps* by ~25%
			- Reduce *max shifts X & Y* by ~25%
			- Reduce *max deviation from rigid* by ~25%

.. _faq-project-organization:

Project Organization
====================
	#. Can I modify a sample?
		- See <link here> *Modify Sample and Overwrite guide*. Double click the Sample ID in the Project Browser to open it in a viewer. You can then make any modifications you want and then go to File -> Add to Project and select the “Save Changes Overwrite” option at the bottom. 

	#. Can I change the SampleID?
		- No this is fundamentally impossible due to the underlying data structure.
		- A work-around is to open that Sample in the viewer (double click it in the project browser), make any modifications if necessary, then go to File -> Add to Project, enter the the information for this sample and a new Animal ID (and Trial ID if wanted), and then select the option “Add to Project Dataframe” at the bottom and click Proceed. This will now add a new Sample to the project with this Sample ID. You can then delete the previous Sample, see <link here> *Project Browser guide*

	#. Can I add a new Custom Column, ROI Column, or Stimulus Column to my project when I already have samples in my project?
		- Yes, just modify your Project Configuration using the exact same GUI that you used when creating your project. In the Welcome Window go to Configure -> Project Configuration. Add anything that you want, and then click “Save and Apply”. It's best to immediately restart Mesmerize whenever you change your project configuration.
		- If you are adding a new Custom Column you can enter a “Dataframe replace value”. This will allow you to set a value for all existing Samples in your project for this new column.
		- If you do not set a Dataframe replace value it will label all existing as “untagged”

		.. seealso:: :ref:`Project Configuration <project-configuration>`

