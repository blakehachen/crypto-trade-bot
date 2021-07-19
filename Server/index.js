const Pool = require('pg').Pool;
const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'api',
    password: '',
    port: 5432,
})
const express = require('express');
const router = express.Router();
const app = express();
app.use(express.urlencoded({extended: true}));
app.use(express.json());
const port = 80;

app.listen(port, () => {
    console.log(`App is running on port ${port}.`)
});

app.post('/api/datasets', (req, res) => {
    
    let {uuid, pair, exchange, periodstart, periodend, candlesize, currency, asset} = req.body
    var removeTstart = String(req.body.periodStart).split('T').join(' ');
    var removeTend = String(req.body.periodEnd).split('T').join(' ');
    var candlesizeconv = String(req.body.candleSize)
    pool.query('INSERT INTO datasets (uuid, pair, exchange, periodstart, periodend, candlesize, currency, asset) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)', [uuid, pair, exchange, removeTstart, removeTend, candlesizeconv, currency, asset], (error, results) => {
        if(error){
            
            throw error
        }
        console.log(req)

        //res.status(201).send(`Dataset Added with ID: ${results.insertId}`)
        
    })
    res.status(201).json(req.body)
});

app.post('/api/prices', (req, res) => {
    let {pair, currency, asset, exchange, lowest, highest, volume, dataset, openat} = req.body
    var openatstr = String(req.body.openAt);
    pool.query('INSERT INTO prices (pair, currency, asset, exchange, lowest, highest, volume, dataset, openat) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)',[pair, currency, asset, exchange, lowest, highest, volume, dataset, openatstr], (error, results) => {
        if(error){
            throw error
        }
        console.log(req)
    })
    
    res.status(201).json(req.body)
});

app.get('/api/datasets', (req, res) => {
    console.log(req)
    

    pool.query('SELECT * FROM datasets', (error, results) =>{
        if(error){
            throw error
        }
        res.status(200).json(results.rows)
    })

    
});

app.get('/api/prices', (req, res) => {
    console.log(req)
    const uuid = '/api/datasets/' + req.body.dataset

    pool.query('SELECT * FROM prices WHERE dataset = $1', [uuid], (error, results) => {
        if(error){
            throw error
        }

        res.status(200).json(results.rows)
    })
});

