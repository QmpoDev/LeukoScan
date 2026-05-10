import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import PredictionPage from '../pages/PredictionPage';

describe('PredictionPage', () => {
    it('renders the drop zone area', () => {
        render(
            <MemoryRouter>
                <PredictionPage />
            </MemoryRouter>
        );
        expect(
            screen.getByRole('button', { name: /drop zone/i })
        ).toBeInTheDocument();
    });

    it('renders the classify button initially disabled', () => {
        render(
            <MemoryRouter>
                <PredictionPage />
            </MemoryRouter>
        );
        const btn = screen.getByRole('button', { name: /run classification/i });
        expect(btn).toBeDisabled();
    });

    it('renders the page heading', () => {
        render(
            <MemoryRouter>
                <PredictionPage />
            </MemoryRouter>
        );
        expect(
            screen.getByRole('heading', { name: /white blood cell classifier/i })
        ).toBeInTheDocument();
    });
});
