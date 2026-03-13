#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cat > "$script_dir/claude" <<'EOF'
#!/bin/sh
if [ "${1:-}" = "--version" ]; then
  echo claude 9.9.9
  exit 0
fi

echo "unsupported command: $*" >&2
exit 1
EOF
chmod +x "$script_dir/claude"
echo "installed fake claude to $script_dir/claude"
