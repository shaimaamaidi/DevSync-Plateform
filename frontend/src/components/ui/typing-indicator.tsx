export function TypingIndicator() {
  return (
    <div className="flex items-center gap-[5px] py-[3px]">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="w-[7px] h-[7px] rounded-full bg-slate-300 animate-bounce"
          style={{
            animationDelay: `${i * 0.18}s`,
          }}
        />
      ))}
    </div>
  );
}