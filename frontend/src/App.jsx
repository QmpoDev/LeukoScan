import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import FeaturesPage from './pages/FeaturesPage';
import PredictionPage from './pages/PredictionPage';

export default function App() {
    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-1">
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/about" element={<AboutPage />} />
                    <Route path="/features" element={<FeaturesPage />} />
                    <Route path="/predict" element={<PredictionPage />} />
                </Routes>
            </main>
        </div>
    );
}
