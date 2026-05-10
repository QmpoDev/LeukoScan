import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Microscope, Menu, X } from 'lucide-react';

const navLinks = [
    { to: '/', label: 'Home' },
    { to: '/about', label: 'About' },
    { to: '/features', label: 'Features' },
    { to: '/predict', label: 'Classify' },
];

export default function Navbar() {
    const [menuOpen, setMenuOpen] = useState(false);

    const linkClass = ({ isActive }) =>
        isActive
            ? 'text-[#1CBDC9] font-semibold'
            : 'text-white/80 hover:text-white transition-colors';

    return (
        <nav className="bg-[#172F7C] text-white shadow-lg sticky top-0 z-50">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">

                    {/* Brand */}
                    <NavLink
                        to="/"
                        className="flex items-center gap-2 text-white hover:text-[#2DC6B2] transition-colors shrink-0"
                    >
                        <Microscope size={22} className="text-[#2DC6B2]" />
                        <span className="font-extrabold text-lg tracking-tight">LeukoScan</span>
                    </NavLink>

                    {/* Desktop links */}
                    <ul className="hidden md:flex items-center gap-1">
                        {navLinks.map(({ to, label }) => (
                            <li key={to}>
                                <NavLink
                                    to={to}
                                    className={({ isActive }) =>
                                        `px-4 py-2 rounded-md text-sm font-medium transition-colors ${isActive
                                            ? 'bg-white/10 text-[#1CBDC9]'
                                            : 'text-white/80 hover:bg-white/10 hover:text-white'
                                        }`
                                    }
                                    end={to === '/'}
                                >
                                    {label}
                                </NavLink>
                            </li>
                        ))}
                        <li className="ml-3">
                            <NavLink
                                to="/predict"
                                className="bg-[#2DC6B2] hover:bg-[#1CBDC9] text-white text-sm font-semibold px-4 py-2 rounded-md transition-colors"
                            >
                                Get Started
                            </NavLink>
                        </li>
                    </ul>

                    {/* Mobile hamburger */}
                    <button
                        className="md:hidden p-2 rounded-md text-white/80 hover:text-white hover:bg-white/10 transition-colors"
                        onClick={() => setMenuOpen((o) => !o)}
                        aria-label="Toggle menu"
                        aria-expanded={menuOpen}
                    >
                        {menuOpen ? <X size={22} /> : <Menu size={22} />}
                    </button>
                </div>
            </div>

            {/* Mobile dropdown */}
            {menuOpen && (
                <div className="md:hidden border-t border-white/10">
                    <ul className="px-4 py-3 flex flex-col gap-1">
                        {navLinks.map(({ to, label }) => (
                            <li key={to}>
                                <NavLink
                                    to={to}
                                    className={({ isActive }) =>
                                        `block px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive
                                            ? 'bg-white/10 text-[#1CBDC9]'
                                            : 'text-white/80 hover:bg-white/10 hover:text-white'
                                        }`
                                    }
                                    end={to === '/'}
                                    onClick={() => setMenuOpen(false)}
                                >
                                    {label}
                                </NavLink>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </nav>
    );
}
