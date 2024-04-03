package main

import (
	"bytes"
	"io"
	"net/http"
	"net/http/httputil"
	"net/url"

	"github.com/gin-gonic/gin"
)

const (
	PERMITTED_ID    = ""
	OPENAI_API_KEY  = ""
	REAL_OPENAI_URL = "https://api.openai.com/v1"
	FAKE_API_KEY    = "fake_api_key" // This would be a randomly generated secret in the real application.
)

// Very basic DLP check that looks for matches from a list of forbidden words.
var FORBIDDEN_WORDS = []string{"passionfruit"}
var reqs = 0
var blocked = 0

type identityProof struct {
	Idproof string `json:"idproof"`
}

func containsSubstring(str, substr string) bool {
	for i := 0; i < len(str)-len(substr)+1; i++ {
		if str[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}

func handleOpenAI(c *gin.Context) {
	reqs += 1

	contents, _ := io.ReadAll(c.Request.Body)
	c.Request.Body = io.NopCloser(bytes.NewReader(contents))
	contentsStr := string(contents)

	// Check for matches with forbidden words
	for _, word := range FORBIDDEN_WORDS {
		if containsSubstring(contentsStr, word) {
			c.JSON(400, gin.H{
				"error": "forbidden",
			})
			blocked += 1
			return
		}
	}

	// Rewrite the fake API key that was sent to the client with a real API key.
	if !containsSubstring(c.Request.Header["Authorization"][0], FAKE_API_KEY) {
		c.JSON(400, gin.H{
			"error": "forbidden",
		})
		blocked += 1
		return
	}

	c.Request.Header["Authorization"] = []string{"Bearer " + OPENAI_API_KEY}
	remote, err := url.Parse(REAL_OPENAI_URL)
	if err != nil {
		panic(err)
	}

	proxy := httputil.NewSingleHostReverseProxy(remote)
	proxy.Director = func(req *http.Request) {
		req.Header = c.Request.Header
		req.Host = remote.Host
		req.URL.Scheme = remote.Scheme
		req.URL.Host = remote.Host
		req.URL.Path = "/v1" + c.Param("proxyPath")
	}

	proxy.ServeHTTP(c.Writer, c.Request)

}
func handleStats(c *gin.Context) {
	c.JSON(200, gin.H{
		"total requests": reqs,
		"blocked":        blocked,
	})
}

func handleAuth(c *gin.Context) {
	var idproof identityProof

	if err := c.BindJSON(&idproof); err != nil {
		c.JSON(400, gin.H{
			"error": "bad identity proof",
		})
		return
	}
	empty := []byte{}
	resp, err := http.Post(idproof.Idproof, "application/json", bytes.NewBuffer(empty))
	if err != nil {
		c.JSON(400, gin.H{
			"error": "bad identity proof",
		})
		return
	}
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		c.JSON(400, gin.H{
			"error": "bad identity proof",
		})
		return
	}
	sb := string(body)
	if containsSubstring(sb, PERMITTED_ID) {
		c.JSON(200, gin.H{
			"key": FAKE_API_KEY,
		})
		return
	} else {
		c.JSON(400, gin.H{
			"error": "bad identity proof",
		})
		return
	}
}

func main() {
	r := gin.Default()
	// These are the main client routes for accessing various APIs.
	// In reality there should be some routing logic here to determine which vendor API to call when.
	// But for now, it's just OpenAI.
	r.Any("/routes/*proxyPath", handleOpenAI)
	// This is the route the client would call to prove their identity and get a fake API key.
	r.Any("/auth", handleAuth)
	// This route can opened in the browser to get some basic request stats.
	r.Any("/stats", handleStats)

	r.Run()
}
