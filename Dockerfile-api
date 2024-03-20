FROM python:3.11-slim-bookworm
ENV USER=sccity
ENV GROUPNAME=$USER
ENV UID=1435
ENV GID=1435
RUN addgroup \
    --gid "$GID" \
    "$GROUPNAME" \
&&  adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --ingroup "$GROUPNAME" \
    --no-create-home \
    --uid "$UID" \
    $USER
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN chown -R sccity:sccity /app && chmod -R 775 /app
USER sccity
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:5000/ || exit 1
CMD ["python", "app.py"]