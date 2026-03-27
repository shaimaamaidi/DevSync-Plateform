type ClassValue =
  | string
  | number
  | boolean
  | null
  | undefined
  | ClassValue[]
  | { [key: string]: boolean };

function cn(...inputs: ClassValue[]): string {
  const classes: string[] = [];

  const push = (input: ClassValue): void => {
    if (!input) return;
    if (typeof input === 'string' || typeof input === 'number') {
      classes.push(String(input));
      return;
    }
    if (Array.isArray(input)) {
      input.forEach(push);
      return;
    }
    if (typeof input === 'object') {
      Object.entries(input).forEach(([key, value]) => {
        if (value) classes.push(key);
      });
    }
  };

  inputs.forEach(push);
  return classes.join(' ');
}

export { cn };
