import type { DependencyList, Dispatch, SetStateAction } from 'react';
import { useEffect, useState } from 'react';

interface AsyncState<T> {
  data: T | null;
  error: string | null;
  isLoading: boolean;
  refresh: () => Promise<void>;
  setData: Dispatch<SetStateAction<T | null>>;
}

export function useAsyncData<T>(loader: () => Promise<T>, dependencies: DependencyList): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function refresh() {
    setIsLoading(true);
    setError(null);
    try {
      const nextData = await loader();
      setData(nextData);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, dependencies);

  return { data, error, isLoading, refresh, setData };
}
