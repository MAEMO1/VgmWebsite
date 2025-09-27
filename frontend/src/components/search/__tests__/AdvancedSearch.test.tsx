import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AdvancedSearch from '../AdvancedSearch';
import type { SearchResult } from '@/types/api';
import { apiClient } from '@/api/client';

jest.mock('@/api/client', () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

const mockSearchResult: SearchResult = {
  mosques: [],
  events: [],
  news: [],
  campaigns: [],
  total_results: 0,
  page: 1,
  per_page: 20,
  total_pages: 0,
};

describe('AdvancedSearch', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('triggers search and returns results', async () => {
    (apiClient.get as jest.Mock).mockResolvedValueOnce(mockSearchResult);
    const onResults = jest.fn();
    const onLoading = jest.fn();
    const onError = jest.fn();

    render(
      <AdvancedSearch
        onResults={onResults}
        onLoading={onLoading}
        onError={onError}
      />
    );

    const [inlineSearchButton, footerSearchButton] = screen.getAllByRole('button', { name: /search/i });
    fireEvent.click(footerSearchButton ?? inlineSearchButton);

    await waitFor(() => expect(apiClient.get).toHaveBeenCalledTimes(1));
    expect(onResults).toHaveBeenCalledWith(mockSearchResult);
    expect(onError).toHaveBeenCalledWith('');
  });

  it('surfaces API errors', async () => {
    (apiClient.get as jest.Mock).mockRejectedValueOnce(new Error('Boom'));
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const onResults = jest.fn();
    const onLoading = jest.fn();
    const onError = jest.fn();

    render(
      <AdvancedSearch
        onResults={onResults}
        onLoading={onLoading}
        onError={onError}
      />
    );

    const [inlineSearchButton, footerSearchButton] = screen.getAllByRole('button', { name: /search/i });
    fireEvent.click(footerSearchButton ?? inlineSearchButton);

    await waitFor(() => expect(onError).toHaveBeenCalledWith('Boom'));
    expect(onResults).not.toHaveBeenCalled();
    consoleSpy.mockRestore();
  });
});
