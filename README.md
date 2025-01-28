# LED Control System with Polylith and Poetry monorepository

## Checklist of Plans :)
- [x] Poetry polylith project structure  
- [x] lde folder that contains simple k8s configurations for  
     - [x] postgres   
     - [x] mongodb   
     - [x] redis   
     - [x] k3d default configuration (port mapings to localhost)  
     - [x] README file with instructions   
- [x] VSCode IDE setup instructions
     - [x] FastAPI examle
     - [x] Django example   
- [x] PyCharm IDE setup instructions
     - [x] FastAPI example
     - [x] Django example   
- [ ] FastAPI examle
     - [x] base example 
     - [ ] project examle
     - [ ] Keycloak client example
- [ ] Django example base 
     - [x] base example 
     - [ ] project examle  
     - [ ] Keycloak client example
- [ ] ReactJS example
     - [ ] base example 
     - [ ] project examle
     - [ ] Keycloak client example
- [ ] VueJS example
     - [ ] base example 
     - [ ] project examle
     - [ ] Keycloak client example
- [ ] Keycloak 
     - [x] base server configuration
     - [ ] authentification configuration
     - [ ] authorization configuration   
      - [] user management configuration   
      - [] role management configuration   
      - [] permission management configuration  
- [ ] Observability 
     - [ ] Logging configuration   
     - [ ] Metrics configuration   
     - [ ] Distributed Tracing configuration    

## Poetry Setup and Installation

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

LDE (Local Development Environment) provides a streamlined environment for managing Kubernetes clusters locally using k3d.

Its primary purpose is to simplify the setup and management of a local Kubernetes cluster for development.

For detailed setup instructions, please refer to the [lde/README.md](lde/README.md) file.

### Key Features of LDE

- Easy creation, starting, and stopping of Kubernetes clusters locally.
- Simple mechanism to delete clusters when they are no longer needed.

## Setting Up Your Integrated Development Environment (IDE)
### VSCode
We have pre-configured settings for VS Code in the `.vscode` folder. This includes:
*   `settings.json`: Extra paths have been added to allow the IDE to navigate and work with our multi-root project structure.
*   `launch.json`: Configuration files are provided to enable debugging FastAPI or Django applications directly from within VS Code.

### PyCharm Setup
Configure your project settings in PyCharm as follows:

1. **Project Structure**:
	* Set "base", "components", and "development" folders as source directories.
2. **Django Support (if applicable)**:
	* Enable Django support to run Django applications from within the IDE.
3. **FastAPI Configuration (if applicable)**:
	* Create a new Run/Debug configuration for FastAPI, setting the application file to `bases/backend/fapi_example/core.py`.

This setup should provide you with a streamlined development environment in PyCharm.
