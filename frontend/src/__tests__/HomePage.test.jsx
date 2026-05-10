import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import HomePage from '../pages/HomePage';

describe('HomePage', () => {
    it('renders the main headline', () => {
        render(
            <MemoryRouter>
                <HomePage />
            </MemoryRouter>
        );
        expect(
            screen.getByRole('heading', { name: /Precision White Blood Cell/i })
        ).toBeInTheDocument();
    });

    it('renders a link to the Prediction page', () => {
        render(
            <MemoryRouter>
                <HomePage />
            </MemoryRouter>
        );
        const links = screen.getAllByRole('link');
        const predictLinks = links.filter((l) => l.getAttribute('href') === '/predict');
        expect(predictLinks.length).toBeGreaterThan(0);
    });
});
