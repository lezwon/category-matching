const createPhantomPool = require('phantom-pool')
const http = require('http')
var url = require('url');

// Returns a generic-pool instance
const pool = createPhantomPool({
  max: 10, // default
  min: 4, // default
  // how long a resource can stay idle in pool before being removed
  idleTimeoutMillis: 30000, // default.
  // maximum number of times an individual resource can be reused before being destroyed; set to 0 to disable
  maxUses: 3, // default
  // function to validate an instance prior to use; see https://github.com/coopernurse/node-pool#createpool
  validator: () => Promise.resolve(true), // defaults to always resolving true
  // validate resource before borrowing; required for `maxUses and `validator`
  testOnBorrow: true, // default
  // For all opts, see opts at https://github.com/coopernurse/node-pool#createpool
  phantomArgs: [['--ignore-ssl-errors=true', '--disk-cache=true', '--ssl-protocol=any'], {
    logLevel: 'debug',
  }], // arguments passed to phantomjs-node directly, default is `[]`. For all opts, see https://github.com/amir20/phantomjs-node#phantom-object-api
})

// Automatically acquires a phantom instance and releases it back to the
// pool when the function resolves or throws

function sleep(ms){
  return new Promise(resolve=>{
      setTimeout(resolve,ms)
  })
}


const port = 3000;

const requestHandler = async (request, response) => {

    pool.use(async (instance) => {
      
      page = await instance.createPage()
      
      // await page.clearCookies();

      // await page.setting('javascriptEnabled', true)
      await page.setting('viewportSize', {width: 1024, height: 768})
      // await page.setting('loadImages', False)
      await page.setting('resourceTimeout', 3500)
      await page.setting('userAgent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36')
      

      await page.property('customHeaders', {
          'authority': 'www.google.com',
          'pragma': 'no-cache',
          'cache-control': 'no-cache',
          'upgrade-insecure-requests': '1',
          'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
          // 'accept-encoding': 'gzip, deflate, br',
          'accept-language': 'en-US,en;q=0.9'
      })

      // await page.on('onLoadFinished', async (status) => {
      //   if(!response.finished){
      //     console.log('ITS LOADED!!')          
      //     const content = await page.property('content')
      //     await response.write(content);
      //     // await page.render('davidwalshblog.png');
      //     response.end()
      //   }
      // });

      var query = request.url.substring(6);
      start_time = Date.now()
      
      console.time(query)
      page.open(query, { operation: 'GET' }).then((status) => {
        return page.property('content')
      }).then(content => {
        console.timeEnd(query)
        response.write(content);
        response.end()
        end_time = Date.now() - start_time
        // console.log(query + " " + end_time)
      })
      .catch((error) => {
        console.log(error)
      })

      // const status = await page.open(query, { operation: 'GET' })
      // if (status !== 'success') {
      //     console.log("cant open")
      // }

      // const content = await page.property('content')
      // await response.write(content);
      // // await page.render('davidwalshblog.png');
      // response.end()
      // end_time = Date.now() - start_time
      // console.log(query + " " + end_time)
    })
}

const server = http.createServer(requestHandler)

server.listen(port, (err) => {
  if (err) {
    return console.log('something bad happened', err)
  }

  console.log(`server is listening on ${port}`)
})


// pool.use(async (instance) => {
//   const page = await instance.createPage()
//   const status = await page.open('http://google.com', { operation: 'GET' })
//   if (status !== 'success') {
//     throw new Error('cannot open google.com')
//   }
//   const content = await page.property('content')
//   return content
// }).then((content) => {
//   console.log(content)
// })

// Destroying the pool:
// pool.drain().then(() => pool.clear())

// For more API doc, see https://github.com/coopernurse/node-pool#generic-pool

