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
	PERMITTED_ID   = "arn:aws:iam::637423479705:user/testUser"
	OPENAI_API_KEY = "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"
)

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
	remote, err := url.Parse("https://api.openai.com/v1")
	if err != nil {
		panic(err)
	}
	reqs += 1

	c.Request.Header["Authorization"] = []string{"Bearer " + OPENAI_API_KEY}

	contents, _ := io.ReadAll(c.Request.Body)
	c.Request.Body = io.NopCloser(bytes.NewReader(contents))
	contentsStr := string(contents)
	for _, word := range FORBIDDEN_WORDS {
		if containsSubstring(contentsStr, word) {
			c.JSON(400, gin.H{
				"error": "forbidden",
			})
			blocked += 1
			return
		}
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
			"key": "api-key",
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
	r.Any("/routes/*proxyPath", handleOpenAI)
	r.Any("/auth", handleAuth)
	r.Any("/stats", handleStats)

	r.Run()
}
