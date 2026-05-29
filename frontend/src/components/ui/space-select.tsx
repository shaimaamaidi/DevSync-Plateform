import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { ClickUpSpaceLightDTO } from '@/api/api';

interface SpaceSelectProps {
  spaces: ClickUpSpaceLightDTO[];
  spacesLoading: boolean;
  disabled?: boolean;
  showRepoBadge?: boolean;
  onSelect: (space: ClickUpSpaceLightDTO) => void;
}

export function SpaceSelect({ spaces, spacesLoading, disabled, showRepoBadge, onSelect }: SpaceSelectProps) {
  const handleValueChange = (value: string) => {
    if (value === 'none') return;
    const space = spaces.find(s => s.space_code === value);
    if (space) onSelect(space);
  };

  return (
    <div className="animate-[msg-in_0.22s_ease-out_both] pl-[36px] sm:pl-[42px]">
      <Select
        value="none"
        onValueChange={handleValueChange}
        disabled={disabled || spacesLoading}
      >
        <SelectTrigger className="w-full sm:w-[320px] bg-input border-border text-foreground">
          <SelectValue
            placeholder={spacesLoading ? 'Loading spaces…' : 'Select a click up space'}
          />
        </SelectTrigger>
        <SelectContent className="bg-card border-border">
          {spacesLoading ? (
            <SelectItem value="none" disabled>
              Loading spaces…
            </SelectItem>
          ) : spaces.length === 0 ? (
            <SelectItem value="none" disabled>
              No ClickUp space available
            </SelectItem>
          ) : (
            <>
              <SelectItem value="none" className="hidden" disabled>
                Select a click up space
              </SelectItem>
              {spaces.map(s => (
                <SelectItem key={s.space_code} value={s.space_code}>
                  <div className="flex items-center gap-2">
                    <span>{s.name}</span>
                    {showRepoBadge && !s.repo && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-600 font-medium leading-none">
                        No github repository linked
                      </span>
                    )}
                    {s.repo && (
                      <span className="text-[10px] text-muted-foreground">
                        🔗 {s.repo.name}
                      </span>
                    )}
                  </div>
                </SelectItem>
              ))}
            </>
          )}
        </SelectContent>
      </Select>
    </div>
  );
}