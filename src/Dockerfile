FROM continuumio/miniconda3

WORKDIR /app
COPY . /app

# Copy and create the environment
COPY _src/frontend/environment.yml ./environment.yml
RUN conda env create -f environment.yml

# Activate env and set it as default
SHELL ["conda", "run", "-n", "ygg", "/bin/bash", "-c"]
ENV PATH /opt/conda/envs/ygg/bin:$PATH

# Optional: make sure the script is executable
RUN chmod +x /app/_src/frontend/start_app.sh

EXPOSE 8501
CMD ["bash", "/app/_src/frontend/start_app.sh"]