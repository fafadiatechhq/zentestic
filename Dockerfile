FROM frappe/erpnext:version-15

USER frappe
WORKDIR /home/frappe/frappe-bench

# Copy the zentestic app source into the bench apps directory
COPY --chown=frappe:frappe . apps/zentestic

# Install the app into the bench's Python virtual environment
RUN /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir \
    -e /home/frappe/frappe-bench/apps/zentestic
