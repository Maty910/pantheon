#!/usr/bin/env bash
set -u
set -o pipefail

names=(athena heimdall hermes iris nemesis odin saga themis thor)
runtime= runtime_seen=0 components= components_seen=0 apply=0 dry=0 backup=0
fail() { printf 'Error: %s\n' "$*" >&2; exit 1; }
while (($#)); do
  case "$1" in
    --runtime) (($# >= 2)) || fail 'missing runtime'; ((runtime_seen == 0)) || fail 'duplicate runtime'; runtime_seen=1; runtime=$2; shift 2 ;;
    --components) (($# >= 2)) || fail 'missing components'; ((components_seen == 0)) || fail 'duplicate components'; components_seen=1; components=$2; shift 2 ;;
    --apply) ((apply == 0)) || fail 'duplicate apply'; apply=1; shift ;;
    --dry-run) ((dry == 0)) || fail 'duplicate dry-run'; dry=1; shift ;;
    --backup) ((backup == 0)) || fail 'duplicate backup'; backup=1; shift ;;
    *) fail "unknown argument: $1" ;;
  esac
done
case "$runtime" in claude|opencode|both) ;; *) fail 'runtime must be claude, opencode or both' ;; esac
agents=0 skills=0 template=0
if (( !components_seen )); then
  agents=1
elif [[ $components == all ]]; then
  agents=1; skills=1; template=1
else
  [[ -n $components && $components != ,* && $components != *, && $components != *,,* ]] || fail 'invalid components list'
  remaining_components=$components
  while :; do
    if [[ $remaining_components == *,* ]]; then
      component=${remaining_components%%,*}; remaining_components=${remaining_components#*,}
    else
      component=$remaining_components; remaining_components=
    fi
    case "$component" in
      agents) ((agents == 0)) || fail 'duplicate component: agents'; agents=1 ;;
      skills) ((skills == 0)) || fail 'duplicate component: skills'; skills=1 ;;
      template) ((template == 0)) || fail 'duplicate component: template'; template=1 ;;
      *) fail "invalid component: $component" ;;
    esac
    [[ -n $remaining_components ]] || break
  done
fi
(( !(apply && dry) )) || fail 'apply and dry-run are incompatible'
(( !backup || apply )) || fail 'backup requires apply'
[[ ${HOME:-} == /* && -d $HOME ]] || fail 'HOME must be an existing absolute directory'
[[ $runtime == claude || ( $agents == 0 && $skills == 0 ) || -z ${XDG_CONFIG_HOME:-} || $XDG_CONFIG_HOME == "$HOME/.config" ]] || fail 'custom XDG_CONFIG_HOME is not supported for OpenCode destinations'

# Reject symlinks and non-directories in every existing path component.
safe_dirs() {
  local path=$1 part remaining current=
  [[ $path == /* ]] || return 1
  remaining=${path#/}
  # Split on slash without treating newlines as record delimiters.
  while [[ -n $remaining ]]; do
    if [[ $remaining == */* ]]; then
      part=${remaining%%/*}
      remaining=${remaining#*/}
    else
      part=$remaining
      remaining=
    fi
    [[ -z $part ]] && continue
    current="$current/$part"
    [[ ! -L $current ]] || return 1
    [[ ! -e $current || -d $current ]] || return 1
  done
}
script=${BASH_SOURCE[0]}
[[ $script == /* ]] || script="$PWD/$script"
safe_dirs "${script%/*}" || fail 'unsafe script ancestor'
[[ -f $script && ! -L $script ]] || fail 'unsafe script'
# Sentinel preserves path newlines; remove only the command's own newline.
root=$(cd -- "${script%/*}" && pwd -P && printf '.') || fail 'cannot determine source root'
root=${root%.}; root=${root%$'\n'}
script="$root/${script##*/}"
safe_dirs "$HOME" || fail 'unsafe HOME ancestor'

revision=unknown
git_ok=0
if command -v git >/dev/null 2>&1 && [[ -e $root/.git ]] && \
   top=$(git -C "$root" rev-parse --show-toplevel 2>/dev/null && printf '.') && \
   top=${top%.} && top=${top%$'\n'} && [[ $top == "$root" ]] && \
   revision=$(git -C "$root" rev-parse --verify 'HEAD^{commit}' 2>/dev/null); then
  git_ok=1
else
  revision=unknown
fi
index_flags_safe() {
  # -v marks assume-unchanged with a lowercase tag and skip-worktree with S.
  # NUL records preserve arbitrary tracked filenames; inspection errors fail closed.
  GIT_OPTIONAL_LOCKS=0 git -C "$root" ls-files -v -z | while IFS= read -r -d '' entry; do
    case ${entry:0:1} in [[:lower:]]|S) exit 1 ;; esac
  done
}
state=unknown
if ((git_ok)); then
  if GIT_OPTIONAL_LOCKS=0 git -C "$root" diff --quiet HEAD -- && GIT_OPTIONAL_LOCKS=0 git -C "$root" diff --cached --quiet; then
    if index_flags_safe; then state=clean; fi
  else state=dirty; fi
fi
printf 'Source revision: %s (%s)\n' "$revision" "$state"
if ((apply)); then
  ((git_ok)) || fail 'apply requires a Git checkout rooted at the script with a valid HEAD'
  [[ $state == clean ]] || fail 'tracked Git changes or unverified index flags block apply (assume-unchanged/skip-worktree are unsupported)'
fi

runtimes=()
[[ $runtime == opencode ]] || runtimes+=(claude)
[[ $runtime == claude ]] || runtimes+=(opencode)
sources=() destinations=() actions=() labels=()
plan_file() {
  local src=$1 dst=$2 label=$3 action=copy
  safe_dirs "${src%/*}" || fail "unsafe source directory: ${src%/*}"
  safe_dirs "${dst%/*}" || fail "unsafe destination directory: ${dst%/*}"
  [[ -f $src && ! -L $src ]] || fail "missing or unsafe source: $src"
  [[ ! -L $dst && ( ! -e $dst || -f $dst ) ]] || fail "unsafe destination: $dst"
  if [[ -e $dst ]]; then
    if cmp -s -- "$src" "$dst"; then action=unchanged
    else
      action=replace
      (( !apply || backup )) || fail "conflict without backup: $dst"
    fi
  fi
  sources+=("$src"); destinations+=("$dst"); actions+=("$action"); labels+=("$label")
}
for selected in "${runtimes[@]}"; do
  if [[ $selected == claude ]]; then destbase="$HOME/.claude"; else destbase="$HOME/.config/opencode"; fi
  if ((agents)); then
    for name in "${names[@]}"; do
      plan_file "$root/agents/$selected/$name.md" "$destbase/agents/$name.md" "$selected/$name.md"
    done
  fi
  if ((skills)); then
    for name in review retro; do
      plan_file "$root/skills/$name/SKILL.md" "$destbase/skills/$name/SKILL.md" "skills/$selected/$name/SKILL.md"
    done
  fi
done
if ((template)); then
  plan_file "$root/templates/pull-request.md" "$HOME/.local/share/pantheon/templates/pull-request.md" 'template/pull-request.md'
fi
if ((apply)); then
  for file in "$script" "${sources[@]}"; do
    rel=${file#"$root"/}
    git -C "$root" ls-files --error-unmatch -- "$rel" >/dev/null 2>&1 || fail "untracked source: $rel"
    git -C "$root" show "HEAD:$rel" | cmp -s - "$file" || fail "source differs from HEAD: $rel"
  done
fi
backup_root="$HOME/.local/state/pantheon/backups"
if ((backup)); then safe_dirs "$backup_root" || fail 'unsafe backup directory'; fi
for i in "${!sources[@]}"; do printf '%s %s -> %s\n' "${actions[i]}" "${labels[i]}" "${destinations[i]}"; done
((apply)) || exit 0

umask 077
completed=0
backup_dir=
on_error() {
  local code=$? j
  trap - ERR
  printf 'Apply failed (exit %s); completed: %s; pending from: %s; backups: %s\n' "$code" "$completed" "${labels[i]:-setup}" "${backup_dir:-none}" >&2
  for j in "${!labels[@]}"; do
    if ((j < completed)); then printf 'completed: %s\n' "${labels[j]}" >&2
    else printf 'pending: %s\n' "${labels[j]}" >&2; fi
  done
  exit 1
}
trap on_error ERR
for i in "${!sources[@]}"; do
  if [[ ${actions[i]} == unchanged ]]; then ((completed+=1)); continue; fi
  if [[ ${actions[i]} == replace ]]; then
    if [[ -z $backup_dir ]]; then
      mkdir -p -m 700 -- "$backup_root"
      backup_dir=$(mktemp -d "$backup_root/install.XXXXXXXXXX")
    fi
    mkdir -p -m 700 -- "$backup_dir/${labels[i]%/*}"
    cp -- "${destinations[i]}" "$backup_dir/${labels[i]}"
    chmod 600 -- "$backup_dir/${labels[i]}"
    printf 'Backup: %s\n' "$backup_dir/${labels[i]}"
  fi
  mkdir -p -- "${destinations[i]%/*}"
  temp=$(mktemp "${destinations[i]%/*}/.pantheon.XXXXXXXXXX")
  cp -- "${sources[i]}" "$temp"
  mv -f -- "$temp" "${destinations[i]}"
  ((completed+=1))
done
trap - ERR
printf 'Apply complete: %s entries; backups: %s\n' "$completed" "${backup_dir:-none}"
