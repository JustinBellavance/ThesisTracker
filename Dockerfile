# Use the official Python image from the Docker Hub
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# Create and set the working directory inside the container
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
COPY uv.lock pyproject.toml /app/
RUN uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Set the default command to run the Django development server
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8080", "thesistrackerdjango.wsgi:application","--access-logfile", "logs/gunicorn_access.log", "--error-logfile", "logs/gunicorn_error.log"]