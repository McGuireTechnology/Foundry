FROM apache/superset:4.1.1

LABEL org.opencontainers.image.title="vortex-superset"
LABEL org.opencontainers.image.description="Custom Superset image for Vortex"

USER root
RUN pip install --no-cache-dir psycopg2-binary
USER superset
