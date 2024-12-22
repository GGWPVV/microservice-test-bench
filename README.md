# dataPipelineExperiments
just an experiment with different lib's

## Setting Up Poetry with Polylith Plugin

This guide will walk you through installing Poetry, setting up the Polylith plugin, and verifying the installation.

To manage dependencies and the project structure, we use [Poetry](https://python-poetry.org/) along with the [Polylith](https://polylith.gitbook.io/polylith/) plugin. Follow these steps to set up your environment:


1Verify that Poetry has been installed successfully:
   ```bash
   poetry --version
   ```

### Adding the Polylith Plugin

The Polylith plugin helps manage modular project structures. Follow the steps below to add it to Poetry:

1. First, ensure you have set up Poetry (refer to the previous section).

2. Use the following command to add the Polylith plugin to Poetry:
   ```bash
   poetry self add poetry-multiproject-plugin
   poetry self add poetry-polylith-plugin
   ```

3. Verify that the plugin is successfully installed:
   ```bash
   poetry self show plugins
   ```

If the "polylith" plugin appears in the list, the installation is complete.


## Setting Up LDE

