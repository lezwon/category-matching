/* eslint-disable no-console */
// import phantom from 'phantom'
// import http from 'http'
// import createPhantomPool from '../src'
const phantom = require('phantom-pool')
const createPhantomPool = require('phantom-pool')
const http = require('http')
var url = require('url');

const startServer = () => new Promise((resolve, reject) => {
  const server = http.createServer((req, res) => {
    res.end('test')
  }).listen((err) => {
    if (err) return reject(err)
    resolve(server)
  })
})

const pool = createPhantomPool({
  maxUses: 3,
  min: 10,
  max: 20
})

/* eslint-disable no-unused-vars */
const noPool = async (url) => {
  const instance = await phantom.create()
  const page = await instance.createPage()
  const status = await page.open(url, { operation: 'GET' })
  if (status !== 'success') throw new Error(status)
  const content = await page.property('content')
  // console.log(content)
  await instance.exit()
}

const withPool = (url) => pool.use(async (instance) => {
  const page = await instance.createPage()
  page.open(url, { operation: 'GET' }).then((status) => {
    console.log(status)
    console.log("Done " + url)
    return page.property('content')
  }).then(result => console.log(result))
  .catch((error) => {
    console.log(error)
  })
  // const status = await page.open(url, { operation: 'GET' })
  // if (status !== 'success') throw new Error(status)
  // const content = await page.property('content')
  // console.log("Done " + url)
})

const benchmark = async (iters) => {
  const server = await startServer()
  const url = 'https://www.google.com/search?tbm=lcl&q=accounting+school New Delhi India'

  console.log('')
  console.log('Starting benchmark with pool')
  for (let i = 0; i < iters; i++) {
    console.time(`pool-${i}`)
    await withPool(`${url}/${i}`)
    console.timeEnd(`pool-${i}`)
  }
  console.log('Done')
}

benchmark(10).then(() => {
  // process.exit(0)
}).catch(console.error)