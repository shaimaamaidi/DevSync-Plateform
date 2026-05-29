export function EditableField({
  value,
  onChange,
  type = 'text',
  options,
  placeholder,
  className = '',
}: {
  value: string;
  onChange: (v: string) => void;
  type?: 'text' | 'textarea' | 'select';
  options?: string[];
  placeholder?: string;
  className?: string;
}) {
  const base =
    'text-sm border border-border rounded-md bg-background px-2 py-1 w-full focus:outline-none focus:ring-2 focus:ring-ring ' +
    className;

  if (type === 'textarea') {
    return (
      <textarea
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className={`${base} resize-none`}
        rows={2}
      />
    );
  }

  if (type === 'select' && options) {
    return (
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className={base}
      >
        {options.map(o => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    );
  }

  return (
    <input
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      className={base}
    />
  );
}