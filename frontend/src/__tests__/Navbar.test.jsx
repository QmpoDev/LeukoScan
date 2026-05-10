import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Navbar from '../components/Navbar';

describe('Navbar', () => {
    it('renders links to all four pages', () => {
        render(
            <MemoryRouter>
                <Navbar />
            </MemoryRouter>
        );
        expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /about/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /features/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /classify/i })).toBeInTheDocument();
    });

    it('renders the LeukoScan brand link', () => {
        render(
            <MemoryRouter>
                <Navbar />
            </MemoryRouter>
        );
        expect(screen.getByRole('link', { name: /leukoscan/i })).toBeInTheDocument();
    });
});
