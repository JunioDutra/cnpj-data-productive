import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Home from './Home';
import MyAdmin from './MyAdmin';

export const App = () => (
    <BrowserRouter>
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/admin/*" element={<MyAdmin />} />
        </Routes>
    </BrowserRouter>
);