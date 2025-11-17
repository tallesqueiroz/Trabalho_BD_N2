import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Clientes from "./pages/Clientes";
import Livros from "./pages/Livros";
import Autores from "./pages/Autores";
import Categorias from "./pages/Categorias";
import Editoras from "./pages/Editoras";
import Exemplares from "./pages/Exemplares";
import Emprestimos from "./pages/Emprestimos";
import MeuPerfil from "./pages/MeuPerfil";
import Dashboard from './pages/Dashboard'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />

        <Route path="/clientes" element={<Clientes />} />
        <Route path="/livros" element={<Livros />} />
        <Route path="/autores" element={<Autores />} />
        <Route path="/categorias" element={<Categorias />} />
        <Route path="/editoras" element={<Editoras />} />
        <Route path="/exemplares/:idLivro" element={<Exemplares />} />
        <Route path="/emprestimos" element={<Emprestimos />} />
        <Route path="/me" element={<MeuPerfil />} />
      </Routes>
    </BrowserRouter>
  );
}

function Home() {
  return <h1>Página principal</h1>;
}
