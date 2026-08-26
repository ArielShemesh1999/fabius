const BOOLEAN_FLAGS = new Set([
  'act', 'yes', 'offline', 'sealed-only', 'remember', 'no-memory', 'json', 'read-only',
  'dangerously-approve-everything', 'ports', 'help', 'version',
]);
const VALUE_FLAGS = new Set([
  'dir', 'provider', 'model', 'tier', 'budget', 'steps', 'checks', 'kind',
  'owner', 'relay', 'allow-origin',
]);
const REPEATABLE_FLAGS = new Set(['owner', 'relay', 'allow-origin']);

const COMMON_RUN = new Set([
  'act', 'yes', 'offline', 'sealed-only', 'no-memory', 'read-only',
  'remember',
  'dangerously-approve-everything', 'dir', 'provider', 'model', 'tier', 'budget',
  'steps', 'allow-origin',
]);
const COMMAND_FLAGS = {
  run: new Set([...COMMON_RUN, 'json']),
  chat: new Set(COMMON_RUN),
  route: new Set(['json', 'provider', 'model', 'tier']),
  recon: new Set(['json', 'ports', 'checks']),
  memory: new Set(['kind']),
  listen: new Set([...COMMON_RUN, 'owner', 'relay']),
  send: new Set(), whoami: new Set(), doctor: new Set(), keys: new Set(),
  version: new Set(), help: new Set(),
};

export function parseArgs(argv) {
  const flags = {};
  const positional = [];
  let options = true;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (options && a === '--') { options = false; continue; }
    if (options && a === '-h') { flags.help = true; continue; }
    if (options && a.startsWith('--')) {
      const eq = a.indexOf('=');
      const key = a.slice(2, eq < 0 ? undefined : eq);
      const inline = eq < 0 ? undefined : a.slice(eq + 1);
      if (!BOOLEAN_FLAGS.has(key) && !VALUE_FLAGS.has(key)) throw new Error(`unknown flag --${key}`);
      let value;
      if (BOOLEAN_FLAGS.has(key)) {
        if (inline !== undefined) throw new Error(`--${key} is a boolean flag and takes no value`);
        value = true;
      } else {
        if (inline !== undefined) value = inline;
        else {
          const next = argv[++i];
          if (next === undefined || next === '--' || next.startsWith('--')) throw new Error(`--${key} requires a value`);
          value = next;
        }
        if (String(value).length === 0) throw new Error(`--${key} requires a non-empty value`);
      }
      if (key in flags && !REPEATABLE_FLAGS.has(key)) throw new Error(`--${key} may be passed only once`);
      flags[key] = REPEATABLE_FLAGS.has(key) && key in flags ? [].concat(flags[key], value) : value;
    } else positional.push(a);
  }
  return { flags, positional };
}

export function validateCommandFlags(command, flags) {
  if (flags.help || flags.version) return;
  const allowed = COMMAND_FLAGS[command];
  if (!allowed) return;
  for (const key of Object.keys(flags)) {
    if (!allowed.has(key)) throw new Error(`--${key} is not valid for ${command}`);
  }
  if (flags['read-only']) {
    const authorityFlags = ['act', 'yes', 'dangerously-approve-everything', 'remember', 'allow-origin']
      .filter((key) => flags[key]);
    if (authorityFlags.length) {
      throw new Error(`--read-only cannot be combined with ${authorityFlags.map((key) => `--${key}`).join(', ')}`);
    }
  }
}

export function positiveNumber(value, name, { integer = false } = {}) {
  if (value === undefined) return undefined;
  const n = Number(value);
  if (!Number.isFinite(n) || n <= 0 || (integer && !Number.isInteger(n))) {
    throw new Error(`--${name} must be a ${integer ? 'positive integer' : 'finite positive number'}`);
  }
  return n;
}

export const CLI_FLAGS = { BOOLEAN_FLAGS, VALUE_FLAGS, REPEATABLE_FLAGS, COMMAND_FLAGS };
