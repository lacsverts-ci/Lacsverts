import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const sessionToken = localStorage.getItem('sessionToken');
    if (sessionToken) {
      setUser({ sessionToken });
    }
    setLoading(false);
  }, []);

  const login = (sessionToken) => {
    localStorage.setItem('sessionToken', sessionToken);
    setUser({ sessionToken });
  };

  const logout = () => {
    localStorage.removeItem('sessionToken');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Navigation Component
const Navigation = () => {
  const { user, logout } = useAuth();
  
  return (
    <nav className="bg-green-600 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
            <span className="text-green-600 font-bold">LV</span>
          </div>
          <span className="text-xl font-bold">Lacs Verts</span>
        </div>
        <div className="flex space-x-6">
          <Link to="/" className="hover:text-green-200 transition-colors">Accueil</Link>
          <Link to="/lakes" className="hover:text-green-200 transition-colors">État des lacs</Link>
          {user && <Link to="/reports" className="hover:text-green-200 transition-colors">Signalement</Link>}
          <Link to="/map" className="hover:text-green-200 transition-colors">Carte</Link>
          <Link to="/awareness" className="hover:text-green-200 transition-colors">Sensibilisation</Link>
        </div>
        <div>
          {user ? (
            <button 
              onClick={logout}
              className="bg-green-700 hover:bg-green-800 px-4 py-2 rounded transition-colors"
            >
              Déconnexion
            </button>
          ) : (
            <a 
              href={`https://auth.emergentagent.com/?redirect=${encodeURIComponent(window.location.origin + '/profile')}`}
              className="bg-green-700 hover:bg-green-800 px-4 py-2 rounded transition-colors"
            >
              Connexion
            </a>
          )}
        </div>
      </div>
    </nav>
  );
};

// Home Component
const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-green-50">
      {/* Hero Section */}
      <div 
        className="relative bg-cover bg-center h-96 flex items-center justify-center"
        style={{
          backgroundImage: 'url("https://images.unsplash.com/photo-1566702258309-9b9edd1235f4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwxfHx3YXRlciUyMHF1YWxpdHl8ZW58MHx8fGJsdWV8MTc1MjQ4NTk0NXww&ixlib=rb-4.1.0&q=85")',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="absolute inset-0 bg-black bg-opacity-40"></div>
        <div className="relative text-center text-white z-10">
          <h1 className="text-5xl font-bold mb-4">Lacs Verts</h1>
          <p className="text-xl mb-6">Pour une vie aquatique saine et durable</p>
          <p className="text-lg">Surveillance et protection des plans d'eau de Côte d'Ivoire</p>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-blue-600 text-2xl">🌊</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">État des lacs</h3>
            <p className="text-gray-600">Consultez l'état de santé de tous les plans d'eau de Côte d'Ivoire</p>
          </div>
          
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-green-600 text-2xl">📍</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">Signalement</h3>
            <p className="text-gray-600">Signalez les problèmes observés sur les lacs avec photos et vidéos</p>
          </div>
          
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-purple-600 text-2xl">🗺️</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">Carte interactive</h3>
            <p className="text-gray-600">Explorez la localisation de tous les lacs sur une carte interactive</p>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-green-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-8">Nos statistiques</h2>
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="text-4xl font-bold">50+</div>
              <div className="text-green-200">Lacs surveillés</div>
            </div>
            <div>
              <div className="text-4xl font-bold">85%</div>
              <div className="text-green-200">Lacs en bon état</div>
            </div>
            <div>
              <div className="text-4xl font-bold">120+</div>
              <div className="text-green-200">Signalements traités</div>
            </div>
            <div>
              <div className="text-4xl font-bold">24/7</div>
              <div className="text-green-200">Surveillance active</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Lakes Status Component
const LakesStatus = () => {
  const [lakes, setLakes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLakes();
  }, []);

  const fetchLakes = async () => {
    try {
      const response = await axios.get(`${API}/lakes`);
      setLakes(response.data);
    } catch (error) {
      console.error('Error fetching lakes:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'propre': return 'bg-green-100 text-green-800';
      case 'à surveiller': return 'bg-yellow-100 text-yellow-800';
      case 'pollué': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'propre': return '✅';
      case 'à surveiller': return '⚠️';
      case 'pollué': return '🚨';
      default: return '❓';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p>Chargement des données...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8">État des lacs de Côte d'Ivoire</h1>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {lakes.map((lake) => (
            <div key={lake.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div 
                className="h-48 bg-cover bg-center"
                style={{
                  backgroundImage: 'url("https://images.unsplash.com/photo-1615874334296-35adc00bf71e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwzfHxsYWtlJTIwbW9uaXRvcmluZ3xlbnwwfHx8Ymx1ZXwxNzUyNDg1OTM3fDA&ixlib=rb-4.1.0&q=85")'
                }}
              />
              <div className="p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-xl font-semibold">{lake.name}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(lake.status)}`}>
                    {getStatusIcon(lake.status)} {lake.status}
                  </span>
                </div>
                <p className="text-gray-600 mb-2">{lake.region}</p>
                <p className="text-gray-700 mb-4">{lake.description}</p>
                <div className="text-sm text-gray-500">
                  <p>Coordonnées: {lake.latitude}°N, {Math.abs(lake.longitude)}°W</p>
                  <p>Dernière mise à jour: {new Date(lake.updated_at).toLocaleDateString('fr-FR')}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Reports Component
const Reports = () => {
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [lakes, setLakes] = useState([]);
  const [formData, setFormData] = useState({
    lake_id: '',
    description: '',
    image_base64: '',
    video_base64: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      fetchReports();
      fetchLakes();
    }
  }, [user]);

  const fetchReports = async () => {
    try {
      const response = await axios.get(`${API}/reports`, {
        headers: { 'X-Session-ID': user.sessionToken }
      });
      setReports(response.data);
    } catch (error) {
      console.error('Error fetching reports:', error);
    }
  };

  const fetchLakes = async () => {
    try {
      const response = await axios.get(`${API}/lakes`);
      setLakes(response.data);
    } catch (error) {
      console.error('Error fetching lakes:', error);
    }
  };

  const handleFileUpload = (e, type) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setFormData(prev => ({
          ...prev,
          [type]: reader.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/reports`, formData, {
        headers: { 'X-Session-ID': user.sessionToken }
      });
      
      alert('Signalement envoyé avec succès!');
      setFormData({
        lake_id: '',
        description: '',
        image_base64: '',
        video_base64: ''
      });
      fetchReports();
    } catch (error) {
      console.error('Error creating report:', error);
      alert('Erreur lors de l\'envoi du signalement');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl mb-4">Veuillez vous connecter pour accéder aux signalements</p>
          <a 
            href={`https://auth.emergentagent.com/?redirect=${encodeURIComponent(window.location.origin + '/profile')}`}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
          >
            Se connecter
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8">Signalement</h1>
        
        {/* Report Form */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Nouveau signalement</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Sélectionner un lac</label>
              <select
                value={formData.lake_id}
                onChange={(e) => setFormData(prev => ({ ...prev, lake_id: e.target.value }))}
                required
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Choisir un lac...</option>
                {lakes.map(lake => (
                  <option key={lake.id} value={lake.id}>{lake.name}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Description du problème</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                required
                rows="4"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Décrivez le problème observé..."
              />
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Photo (optionnel)</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleFileUpload(e, 'image_base64')}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Vidéo (optionnel)</label>
                <input
                  type="file"
                  accept="video/*"
                  onChange={(e) => handleFileUpload(e, 'video_base64')}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Envoi en cours...' : 'Envoyer le signalement'}
            </button>
          </form>
        </div>
        
        {/* Reports List */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Signalements récents</h2>
          <div className="space-y-4">
            {reports.map((report) => (
              <div key={report.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold">{lakes.find(l => l.id === report.lake_id)?.name}</h3>
                  <span className="text-sm text-gray-500">
                    {new Date(report.created_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>
                <p className="text-gray-700 mb-4">{report.description}</p>
                <div className="flex gap-4">
                  {report.image_base64 && (
                    <img 
                      src={report.image_base64} 
                      alt="Signalement" 
                      className="w-24 h-24 object-cover rounded-lg"
                    />
                  )}
                  {report.video_base64 && (
                    <video 
                      src={report.video_base64} 
                      className="w-24 h-24 object-cover rounded-lg"
                      controls
                    />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Map Component
const Map = () => {
  const [lakes, setLakes] = useState([]);
  const [selectedLake, setSelectedLake] = useState(null);

  useEffect(() => {
    fetchLakes();
  }, []);

  const fetchLakes = async () => {
    try {
      const response = await axios.get(`${API}/lakes`);
      setLakes(response.data);
    } catch (error) {
      console.error('Error fetching lakes:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8">Carte des lacs</h1>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-6">
            <p className="text-gray-600 mb-4">
              Cliquez sur un lac dans la liste pour voir ses détails et sa localisation approximative.
            </p>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {lakes.map((lake) => (
                <button
                  key={lake.id}
                  onClick={() => setSelectedLake(lake)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    selectedLake?.id === lake.id 
                      ? 'border-green-500 bg-green-50' 
                      : 'border-gray-200 hover:border-green-300'
                  }`}
                >
                  <h3 className="font-semibold">{lake.name}</h3>
                  <p className="text-sm text-gray-600">{lake.region}</p>
                  <p className="text-xs text-gray-500">
                    {lake.latitude}°N, {Math.abs(lake.longitude)}°W
                  </p>
                </button>
              ))}
            </div>
          </div>
          
          {selectedLake && (
            <div className="border-t pt-6">
              <h2 className="text-xl font-semibold mb-4">Détails du lac sélectionné</h2>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-lg mb-2">{selectedLake.name}</h3>
                <p className="text-gray-700 mb-2">{selectedLake.description}</p>
                <p className="text-sm text-gray-600 mb-2">Région: {selectedLake.region}</p>
                <p className="text-sm text-gray-600 mb-2">
                  Coordonnées: {selectedLake.latitude}°N, {Math.abs(selectedLake.longitude)}°W
                </p>
                <div className="mt-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    selectedLake.status === 'propre' ? 'bg-green-100 text-green-800' :
                    selectedLake.status === 'à surveiller' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    État: {selectedLake.status}
                  </span>
                </div>
              </div>
              
              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  💡 Prochaine mise à jour: Intégration de la carte interactive OpenStreetMap avec marqueurs précis pour chaque lac.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Awareness Component
const Awareness = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await axios.get(`${API}/awareness`);
      setPosts(response.data);
    } catch (error) {
      console.error('Error fetching awareness posts:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p>Chargement des contenus...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8">Sensibilisation</h1>
        
        <div className="space-y-8">
          {posts.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-xl text-gray-600">Aucun contenu de sensibilisation pour le moment.</p>
            </div>
          ) : (
            posts.map((post) => (
              <article key={post.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                {post.image_base64 && (
                  <img 
                    src={post.image_base64} 
                    alt={post.title}
                    className="w-full h-64 object-cover"
                  />
                )}
                <div className="p-6">
                  <h2 className="text-2xl font-bold mb-2">{post.title}</h2>
                  <div className="text-sm text-gray-500 mb-4">
                    Par {post.author_name} • {new Date(post.created_at).toLocaleDateString('fr-FR')}
                  </div>
                  <div className="prose prose-lg max-w-none">
                    {post.content.split('\n').map((paragraph, index) => (
                      <p key={index} className="mb-4">{paragraph}</p>
                    ))}
                  </div>
                  {post.video_base64 && (
                    <div className="mt-4">
                      <video 
                        src={post.video_base64} 
                        className="w-full rounded-lg"
                        controls
                      />
                    </div>
                  )}
                </div>
              </article>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// Profile Component (for auth callback)
const Profile = () => {
  const { login } = useAuth();
  
  useEffect(() => {
    const handleAuth = async () => {
      const hash = window.location.hash;
      const params = new URLSearchParams(hash.substring(1));
      const sessionId = params.get('session_id');
      
      if (sessionId) {
        try {
          const response = await axios.post(`${API}/auth/profile`, {}, {
            headers: { 'X-Session-ID': sessionId }
          });
          
          login(sessionId);
          window.location.href = '/';
        } catch (error) {
          console.error('Authentication failed:', error);
          alert('Erreur d\'authentification');
        }
      }
    };
    
    handleAuth();
  }, [login]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
        <p>Authentification en cours...</p>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Navigation />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/lakes" element={<LakesStatus />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/map" element={<Map />} />
            <Route path="/awareness" element={<Awareness />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;