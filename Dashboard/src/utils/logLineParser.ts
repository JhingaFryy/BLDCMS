export type LogSeverity = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';

export interface ParsedLogLine {
  raw: string;
  timestamp: string | null;
  severity: LogSeverity | null;
  logger: string | null;
  message: string;
}

const KNOWN_SEVERITIES: LogSeverity[] = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];

// Matches every existing file-based log category's shared format (app/core/logging.py's
// LOG_FORMAT): "2026-07-16 10:35:18 | INFO     | app.otp | message text".
const PIPE_FORMAT = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\|\s*(\w+)\s*\|\s*([\w.]+)\s*\|\s*(.*)$/;

// Matches the new Vite Connection Logs format (app/core/logging.py's _vite_formatter):
// "[2026-07-16 10:35:18 IST] INFO [Dashboard] message text".
const BRACKET_FORMAT = /^\[(.+?) IST\]\s*(\w+)\s*(.*)$/;

/**
 * Module 43: several log categories (security, api, auth, otp, activity, digital_signature)
 * switched to JSON-lines structured logging - lines matching neither PIPE_FORMAT nor
 * BRACKET_FORMAT are tried as JSON before falling back to plain text, so severity badges/filters
 * keep working for those categories instead of silently going blank.
 */
function tryParseJsonLine(line: string): ParsedLogLine | null {
  let parsed: unknown;
  try {
    parsed = JSON.parse(line);
  } catch {
    return null;
  }
  if (!parsed || typeof parsed !== 'object') return null;

  const obj = parsed as Record<string, unknown>;
  const rawSeverity = typeof obj.level === 'string' ? obj.level.toUpperCase() : '';
  const severity = KNOWN_SEVERITIES.find((s) => s === rawSeverity) ?? null;
  return {
    raw: line,
    timestamp: typeof obj.timestamp === 'string' ? obj.timestamp : null,
    severity,
    logger: typeof obj.logger === 'string' ? obj.logger : null,
    message: typeof obj.message === 'string' ? obj.message : line,
  };
}

/**
 * Module 33.1: parses a raw log line from EITHER existing format (the module says "the UI should
 * match the existing log viewer" while also wanting search/filter/severity badges - the only way
 * to have both is to make the shared viewer understand both line formats already in use, rather
 * than a Vite-specific viewer). Lines that match neither format (or an unexpected future format)
 * fall back to `severity: null` and render as plain text with no badge - existing categories'
 * content/behavior is unchanged, this only adds an optional parsing layer on top for display.
 */
export function parseLogLine(line: string): ParsedLogLine {
  const pipeMatch = line.match(PIPE_FORMAT);
  if (pipeMatch) {
    const [, timestamp, rawSeverity, logger, message] = pipeMatch;
    const severity = KNOWN_SEVERITIES.find((s) => s === rawSeverity.toUpperCase()) ?? null;
    return { raw: line, timestamp, severity, logger, message };
  }

  const bracketMatch = line.match(BRACKET_FORMAT);
  if (bracketMatch) {
    const [, timestamp, rawSeverity, message] = bracketMatch;
    const severity = KNOWN_SEVERITIES.find((s) => s === rawSeverity.toUpperCase()) ?? null;
    return { raw: line, timestamp: `${timestamp} IST`, severity, logger: null, message };
  }

  const jsonParsed = tryParseJsonLine(line);
  if (jsonParsed) return jsonParsed;

  return { raw: line, timestamp: null, severity: null, logger: null, message: line };
}
