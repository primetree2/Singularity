type Props = {
  score: number;
};

export default function VisibilityScoreBadge({ score }: Props) {
  const color =
    score >= 80
      ? "bg-green-600"
      : score >= 60
      ? "bg-yellow-500"
      : score >= 40
      ? "bg-orange-500"
      : "bg-red-600";

  return (
    <span className={`rounded-full px-3 py-1 text-sm text-white ${color}`}>
      Visibility: {score}%
    </span>
  );
}
