var express = require('express');
const axios = require('axios');
var i18n = require('i18n');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');

var routes = require('./routes/index');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(i18n.init);
app.use(express.static(path.join(__dirname, 'public')));




app.use(logger('dev'));
async function getChainBlocks(port) {
  try {
    const response = await axios.get(`http://192.168.10.58:${port}/chain`);
    const blocks = response.data.chain;
    return blocks
  } catch (error) {
    console.error('Error fetching blocks:', error);
  }
}

async function getHashedBlock(block, port){
  try {
    const response = await axios.post(`http://192.168.10.58:${port}/hash`, block);
    block.hash = response.data.hash;
    return block
  } catch (error) {
    console.error('Error fetching blocks:', error);
  }
}
async function getHashedBlocksFromChain(port) {
  const blocks = await getChainBlocks(port)
  console.log(`retrieved ${blocks.length} blocks from blockchain`)
  return await Promise.all(blocks.map(block => getHashedBlock(block, 5001)));
}
const pug = require('pug');
app.post('/render-block', (req, res) => {
  const { block } = req.body;
  const compiledFunction = pug.compileFile('./views/includes/block.pug');

  const html = compiledFunction({ block });
  res.json({ html });
});

app.get("/blockchain", async (req, res) => {
  console.log("loading blockchain");
  const hashedBlocks = await getHashedBlocksFromChain(5001);
  res.render('blockchain', { chainBlocks: hashedBlocks });
})

app.use('/', routes);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handlers

// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
  app.use(function(err, req, res, next) {
    res.status(err.status || 500);
    res.render('error', {
      message: err.message,
      error: err
    });
  });
}

// production error handler
// no stacktraces leaked to user
app.use(function(err, req, res, next) {
  res.status(err.status || 500);
  res.render('error', {
    message: err.message,
    error: {}
  });
});

i18n.configure({
  locales:['en', 'de', 'es', 'fr-CA', 'hi', 'ja', 'ko', 'nl', 'pl', 'pt', 'zh-CN', 'hu', 'id'],
  directory: __dirname + '/locales'
});


module.exports = app;
