import express from 'express';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use((_, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', 'http://localhost:5173');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (process.env.NODE_ENV !== 'production' && _.method === 'OPTIONS') {
    return res.sendStatus(204);
  }
  next();
});

const recipes = [
  {
    id: 1,
    title: 'Pasta Primavera',
    author: 'Demo User',
    description: 'A bright and fresh pasta packed with seasonal vegetables.',
    prepTime: '20 min',
    difficulty: 'Easy'
  },
  {
    id: 2,
    title: 'Coconut Curry Noodles',
    author: 'Mina',
    description: 'Creamy noodles with a gentle spice and crisp herbs.',
    prepTime: '25 min',
    difficulty: 'Medium'
  },
  {
    id: 3,
    title: 'Honey Lemon Salmon',
    author: 'Theo',
    description: 'A quick dinner with caramelized edges and a citrus glaze.',
    prepTime: '15 min',
    difficulty: 'Easy'
  }
];

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', message: 'Recipe API is running' });
});

app.get('/api/recipes', (_req, res) => {
  res.json(recipes);
});

app.listen(PORT, () => {
  console.log(`Backend listening on http://localhost:${PORT}`);
});
