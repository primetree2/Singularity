import { useState } from "react";

export default function useVisibility() {
  const [score, setScore] = useState<number | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const calculateVisibility = async (lat: number, lon: number) => {
    try {
      setIsCalculating(true);
      // TODO: integrate with backend visibility API
      const simulated = Math.floor(Math.random() * 101);
      await new Promise((res) => setTimeout(res, 500));
      setScore(simulated);
    } catch {
      setScore(null);
    } finally {
      setIsCalculating(false);
    }
  };

  const reset = () => setScore(null);

  return { score, isCalculating, calculateVisibility, reset };
}
