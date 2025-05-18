const jose = require('jose')
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const JWK_URI = process.env.JWK_URI || 'http://localhost:8000/realms/apps/protocol/openid-connect/certs';
const ISSUER = process.env.ISSUER || 'http://localhost:8000/realms/apps';
const AUDIENCE = process.env.AUDIENCE || 'app';
const TARGET_API = process.env.TARGET_API || 'http://192.168.2.185:3000/';
const ENABLE_AUTH = process.env.ENABLE_AUTH || 'true';

const app = express();
const JWKS = jose.createRemoteJWKSet(new URL(JWK_URI));

const middlewareNoAuth = async (proxyReq, req, res) => {
    proxyReq.removeHeader('Authorization');
}

const middlewareAuth = async (proxyReq, req, res) => {
    const auth = req.headers.authorization;
    proxyReq.removeHeader('Authorization');

    try {
        const jwt = auth.split(' ')[1];
        await validate_token(jwt);
    } catch (error) {
        console.log('Token validation error:', error.message);
        if (!res.headersSent) {
            res.status(401).json({ error: 'Unauthorized' });
        }
        proxyReq.destroy();
        return;
    }
}

async function validate_token(jwt) {
    await jose.jwtVerify(jwt, JWKS, {
        issuer: ISSUER,
        audience: AUDIENCE
    })

    const token = jose.decodeJwt(jwt);
    const roles = token?.["resource_access"]?.["app"]?.["roles"] || [];

    if (!roles.includes('admin')) {
        throw new Error('Unauthorized');
    }
}

app.use('/', createProxyMiddleware({
    target: TARGET_API,
    changeOrigin: false,
    onProxyReq: ENABLE_AUTH === 'true' ? middlewareAuth : middlewareNoAuth,},
));

app.listen(3001);
