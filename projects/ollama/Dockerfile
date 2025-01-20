FROM nvidia/cuda:12.6.3-runtime-ubuntu24.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama (replace with actual installation steps)
RUN curl -fsSL https://ollama.com/install.sh | sh

# # Preload your model
# COPY path/to/your/model /ollama/models/

# # Set environment variables
# ENV MODEL_PATH=/ollama/models/your-model

# Expose necessary ports
EXPOSE 11434

# Define the entrypoint
ENTRYPOINT ["ollama", "serve", "--model", "/ollama/models/your-model"]
