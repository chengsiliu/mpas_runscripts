#!/bin/bash

# 1. Save your YAML block to a temporary file
cat <<'EOF' > /tmp/block.yaml
        - localization method: Vertical localization
          vertical lengthscale: 6e3
          ioda vertical coordinate: height
          ioda vertical coordinate group: MetaData
          localization function: Gaspari Cohn
EOF

# 2. Use the 'r' command to read that file for EVERY match
# The 'r' command is specifically designed to handle multiple matches 
# when reading from a physical file.
sed -i '/obs localizations:/r /tmp/block.yaml' test.yaml

# 3. Clean up
rm /tmp/block.yaml

