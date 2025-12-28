#!/bin/sh
# Mindwork Plugin Installation Script
# Workaround for https://github.com/anthropics/claude-code/issues/15178
#
# Usage:
#   ./install.sh              Install skills to ~/.claude/skills/
#   ./install.sh --uninstall  Remove installed skills

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located (plugin root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_NAME="mindwork"

# Target directories
CLAUDE_DIR="$HOME/.claude"
SKILLS_DIR="$CLAUDE_DIR/skills"
COMMANDS_DIR="$CLAUDE_DIR/commands"
AGENTS_DIR="$CLAUDE_DIR/agents"

print_status() {
    printf "${BLUE}[*]${NC} %s\n" "$1"
}

print_success() {
    printf "${GREEN}[+]${NC} %s\n" "$1"
}

print_warning() {
    printf "${YELLOW}[!]${NC} %s\n" "$1"
}

print_error() {
    printf "${RED}[-]${NC} %s\n" "$1"
}

install_skills() {
    print_status "Installing skills..."

    # Create skills directory if it doesn't exist
    if [ ! -d "$SKILLS_DIR" ]; then
        mkdir -p "$SKILLS_DIR"
        print_success "Created $SKILLS_DIR"
    fi

    # Check if skills directory exists in plugin
    if [ ! -d "$SCRIPT_DIR/skills" ]; then
        print_warning "No skills directory found in plugin"
        return
    fi

    # Copy each skill with mindwork- prefix and update SKILL.md
    for skill_path in "$SCRIPT_DIR/skills"/*; do
        if [ -d "$skill_path" ]; then
            skill_name=$(basename "$skill_path")
            new_skill_name="${PLUGIN_NAME}-${skill_name}"
            target="$SKILLS_DIR/$new_skill_name"

            if [ -d "$target" ]; then
                # Check if it's our installation by looking for .mindwork-installed marker
                if [ -f "$target/.mindwork-installed" ]; then
                    # Remove and reinstall to get latest changes
                    rm -rf "$target"
                    print_status "Updating: $new_skill_name"
                else
                    print_error "Cannot install $new_skill_name: $target already exists (not managed by this installer)"
                    continue
                fi
            fi

            # Copy the skill directory
            cp -r "$skill_path" "$target"

            # Update the name in SKILL.md frontmatter
            if [ -f "$target/SKILL.md" ]; then
                # Use sed to replace the name field in frontmatter
                # Match "name: <old_name>" and replace with "name: <new_name>"
                sed -i "s/^name: *${skill_name}$/name: ${new_skill_name}/" "$target/SKILL.md"
            fi

            # Create marker file to identify our installations
            echo "Installed by mindwork install.sh on $(date)" > "$target/.mindwork-installed"

            print_success "Installed: $new_skill_name"
        fi
    done
}

install_commands() {
    # Check if commands directory exists in plugin
    if [ ! -d "$SCRIPT_DIR/commands" ]; then
        return
    fi

    print_status "Installing commands..."

    # Create commands directory if it doesn't exist
    if [ ! -d "$COMMANDS_DIR" ]; then
        mkdir -p "$COMMANDS_DIR"
        print_success "Created $COMMANDS_DIR"
    fi

    # Copy each command with mindwork- prefix
    for cmd_path in "$SCRIPT_DIR/commands"/*.md; do
        if [ -f "$cmd_path" ]; then
            cmd_name=$(basename "$cmd_path" .md)
            new_cmd_name="${PLUGIN_NAME}-${cmd_name}"
            target="$COMMANDS_DIR/${new_cmd_name}.md"

            if [ -f "$target" ]; then
                # Check for our marker comment
                if grep -q "^<!-- mindwork-installed -->" "$target" 2>/dev/null; then
                    rm "$target"
                    print_status "Updating: $new_cmd_name"
                else
                    print_error "Cannot install $new_cmd_name: $target already exists"
                    continue
                fi
            fi

            # Copy and add marker
            {
                echo "<!-- mindwork-installed -->"
                cat "$cmd_path"
            } > "$target"

            print_success "Installed command: $new_cmd_name"
        fi
    done
}

install_agents() {
    # Check if agents directory exists in plugin
    if [ ! -d "$SCRIPT_DIR/agents" ]; then
        return
    fi

    print_status "Installing agents..."

    # Create agents directory if it doesn't exist
    if [ ! -d "$AGENTS_DIR" ]; then
        mkdir -p "$AGENTS_DIR"
        print_success "Created $AGENTS_DIR"
    fi

    # Copy each agent with mindwork- prefix
    for agent_path in "$SCRIPT_DIR/agents"/*.md; do
        if [ -f "$agent_path" ]; then
            agent_name=$(basename "$agent_path" .md)
            new_agent_name="${PLUGIN_NAME}-${agent_name}"
            target="$AGENTS_DIR/${new_agent_name}.md"

            if [ -f "$target" ]; then
                # Check for our marker comment
                if grep -q "^<!-- mindwork-installed -->" "$target" 2>/dev/null; then
                    rm "$target"
                    print_status "Updating: $new_agent_name"
                else
                    print_error "Cannot install $new_agent_name: $target already exists"
                    continue
                fi
            fi

            # Copy and add marker
            {
                echo "<!-- mindwork-installed -->"
                cat "$agent_path"
            } > "$target"

            print_success "Installed agent: $new_agent_name"
        fi
    done
}

uninstall() {
    print_status "Uninstalling ${PLUGIN_NAME} plugin..."

    # Remove skill directories (only those with our marker)
    if [ -d "$SKILLS_DIR" ]; then
        for target in "$SKILLS_DIR/${PLUGIN_NAME}-"*; do
            if [ -d "$target" ] && [ -f "$target/.mindwork-installed" ]; then
                rm -rf "$target"
                print_success "Removed: $(basename "$target")"
            fi
        done
    fi

    # Remove command files (only those with our marker)
    if [ -d "$COMMANDS_DIR" ]; then
        for target in "$COMMANDS_DIR/${PLUGIN_NAME}-"*.md; do
            if [ -f "$target" ] && grep -q "^<!-- mindwork-installed -->" "$target" 2>/dev/null; then
                rm "$target"
                print_success "Removed: $(basename "$target")"
            fi
        done
    fi

    # Remove agent files (only those with our marker)
    if [ -d "$AGENTS_DIR" ]; then
        for target in "$AGENTS_DIR/${PLUGIN_NAME}-"*.md; do
            if [ -f "$target" ] && grep -q "^<!-- mindwork-installed -->" "$target" 2>/dev/null; then
                rm "$target"
                print_success "Removed: $(basename "$target")"
            fi
        done
    fi

    print_success "Uninstallation complete!"
}

install() {
    print_status "Installing ${PLUGIN_NAME} plugin..."
    print_status "Plugin location: $SCRIPT_DIR"
    echo ""

    install_skills
    install_commands
    install_agents

    echo ""
    print_success "Installation complete!"
    echo ""
    print_status "Restart Claude Code to use the new skills:"
    echo "  - mindwork-analyze"
    echo "  - mindwork-insights"
    echo "  - mindwork-progress"
    echo "  - mindwork-summary"
    echo "  - mindwork-transcribe"
    echo ""
    print_status "To update after changes, run ./install.sh again"
}

# Main
case "${1:-}" in
    --uninstall|-u)
        uninstall
        ;;
    --help|-h)
        echo "Mindwork Plugin Installation Script"
        echo ""
        echo "Usage:"
        echo "  ./install.sh              Install/update skills to ~/.claude/"
        echo "  ./install.sh --uninstall  Remove installed skills"
        echo "  ./install.sh --help       Show this help"
        echo ""
        echo "This script copies skills to ~/.claude/skills/ and updates"
        echo "the SKILL.md frontmatter to use the mindwork- prefix."
        echo ""
        echo "Run again after making changes to update the installation."
        ;;
    "")
        install
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
