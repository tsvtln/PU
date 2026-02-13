#!/bin/bash
# shellcheck disable=SC2046
# shellcheck disable=SC2086
# shellcheck disable=SC2059

: <<'END_COMMENT'
This script creates the structure for an ansible project.
Use caution what is your current dir as this can be destructive and
    doesnt have any checks implemented; it will override any
    existing files.

@tsvtln
END_COMMENT

lc(){
    case "$1" in
        [A-Z])
        n=$(printf "%d" "'$1")
        n=$((n+32))
        printf \\$(printf "%o" "$n")
        ;;
        *)
        printf "%s" "$1"
        ;;
    esac
}

dirname="${PWD##*/}"
lwc=''
for((i=0;i<${#dirname};i++))
do
    ch="${dirname:$i:1}"
    lwc+=$(lc "$ch")
done

mkdir ./roles
mkdir ./roles/$lwc
mkdir ./roles/$lwc/defaults
mkdir ./roles/$lwc/files
mkdir ./roles/$lwc/handlers
mkdir ./roles/$lwc/meta
mkdir ./roles/$lwc/tasks
touch ./README.md
touch ./CHANGELOG.md
touch ./main.yml
curl -k -o ./.gitignore "https://raw.githubusercontent.com/tsvtln/PU/refs/heads/main/gitignore"

echo -e "---\n# defaults file for $lwc" > ./roles/$lwc/defaults/main.yml
echo -e "---\n# handlers file for $lwc" > ./roles/$lwc/handlers/main.yml
echo -e "galaxy_info:\n  author: tsvtln\n  description: <fill>\n  company: tsvtln@github\n  license: GPLv2\n  min_ansible_version: '2.4'\n  galaxy_tags: []\n  platforms:\n    - name: EL\n      versions:\n        - all\n    - name: Ubuntu\n      versions:\n        - all\n    - name: Windows\n      versions:\n        - all\ndependencies: []" > ./roles/$lwc/meta/main.yml
echo -e "---" > ./roles/$lwc/tasks/main.yml

echo "ggwp"
