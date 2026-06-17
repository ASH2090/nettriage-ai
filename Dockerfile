# ---------- Stage 1: Builder ----------
# This stage installs dependencies into a clean, isolated location.
# Build tools and pip caches used here never make it into the final image.
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

# Install into a local user directory so we can cleanly copy just the
# installed packages into the final stage, without venv/pip metadata bloat.
RUN pip install --no-cache-dir --user -r requirements.txt gunicorn


# ---------- Stage 2: Final runtime image ----------
# This is the actual image that gets deployed. It only contains what's
# needed to RUN the app — no build tools, no pip cache, smaller and safer.
FROM python:3.11-slim

WORKDIR /app

# Create a dedicated non-root user/group, WITH a proper home directory
# (-m creates /home/appuser and sets correct ownership/permissions on it,
# which gunicorn needs to write its control socket files into)
RUN groupadd -r appuser && useradd -r -m -g appuser appuser

# Copy installed packages from the builder stage into the SAME relative
# path (.local) under the new user's home directory
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Make sure the non-root user owns the app directory and their ENTIRE
# home directory (covers .local AND anything gunicorn needs to write,
# like its control socket folder)
RUN chown -R appuser:appuser /app /home/appuser

# Switch to the non-root user for everything from here on
USER appuser

# Make sure Python can find the packages installed to the user's home dir
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 5000

# Docker periodically hits this to confirm the container is actually healthy,
# not just "running" — reuses the health-check route already built in app.py
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]