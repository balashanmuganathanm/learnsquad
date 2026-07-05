import { useEffect, useState } from 'react';

function App() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('http://localhost:3000/api/recipes')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Unable to load recipes');
        }
        return res.json();
      })
      .then((data) => {
        setRecipes(data);
        setLoading(false);
      })
      .catch(() => {
        setError('We could not load the latest recipes right now.');
        setLoading(false);
      });
  }, []);

  return (
    <main style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #fff7ed 0%, #fef3c7 100%)', padding: '2rem 1rem' }}>
      <div style={{ maxWidth: '960px', margin: '0 auto' }}>
        <header style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div>
            <p style={{ margin: '0 0 0.25rem', textTransform: 'uppercase', letterSpacing: '0.2em', color: '#b45309', fontSize: '0.8rem', fontWeight: 700 }}>
              Community kitchen
            </p>
            <h1 style={{ margin: 0, fontSize: '2rem', color: '#111827' }}>Recipe Feed</h1>
            <p style={{ margin: '0.35rem 0 0', color: '#4b5563', maxWidth: '640px' }}>
              Discover favorite dishes, quick dinners, and seasonal inspiration from fellow home cooks.
            </p>
          </div>
          <button
            style={{ border: 'none', borderRadius: '999px', padding: '0.75rem 1rem', background: '#111827', color: '#fff', cursor: 'pointer' }}
            type="button"
          >
            + Share a recipe
          </button>
        </header>

        {loading ? (
          <div style={{ background: '#fff', borderRadius: '16px', padding: '1.5rem', boxShadow: '0 10px 30px rgba(0,0,0,0.06)' }}>
            <p style={{ margin: 0, color: '#4b5563' }}>Loading recipes...</p>
          </div>
        ) : error ? (
          <div style={{ background: '#fff', borderRadius: '16px', padding: '1.5rem', boxShadow: '0 10px 30px rgba(0,0,0,0.06)' }}>
            <p style={{ margin: 0, color: '#b91c1c' }}>{error}</p>
          </div>
        ) : recipes.length === 0 ? (
          <div style={{ background: '#fff', borderRadius: '16px', padding: '1.5rem', boxShadow: '0 10px 30px rgba(0,0,0,0.06)' }}>
            <p style={{ margin: 0, color: '#4b5563' }}>No recipes yet. Be the first to share one.</p>
          </div>
        ) : (
          <section style={{ display: 'grid', gap: '1rem' }}>
            {recipes.map((recipe) => (
              <article
                key={recipe.id}
                style={{ border: '1px solid #f3d7b5', borderRadius: '20px', padding: '1.25rem', background: '#fff', boxShadow: '0 10px 30px rgba(0,0,0,0.05)' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
                  <div>
                    <h2 style={{ margin: '0 0 0.25rem', fontSize: '1.2rem', color: '#111827' }}>{recipe.title}</h2>
                    <p style={{ margin: 0, color: '#6b7280' }}>by {recipe.author}</p>
                  </div>
                  <span style={{ background: '#fef3c7', color: '#92400e', padding: '0.35rem 0.75rem', borderRadius: '999px', fontSize: '0.85rem', fontWeight: 600 }}>
                    {recipe.difficulty}
                  </span>
                </div>
                <p style={{ margin: '0.8rem 0', color: '#374151', lineHeight: 1.6 }}>{recipe.description}</p>
                <div style={{ display: 'flex', gap: '1rem', color: '#6b7280', fontSize: '0.95rem', flexWrap: 'wrap' }}>
                  <span>⏱ {recipe.prepTime}</span>
                  <span>🍽 Beginner friendly</span>
                </div>
              </article>
            ))}
          </section>
        )}
      </div>
    </main>
  );
}

export default App;
