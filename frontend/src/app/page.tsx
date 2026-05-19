"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Loader2, Send, Video, MessageSquare, ImageIcon, ExternalLink, RefreshCw } from "lucide-react";

const API_BASE = "http://localhost:8000";
const WS_BASE = "ws://localhost:8000";

interface Source {
  timestamp: string;
  frame_url: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export default function VidRAGApp() {
  const [url, setUrl] = useState("");
  const [interval, setIntervalValue] = useState(30);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "ingesting" | "ready" | "error">("idle");
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const startIngestion = async () => {
    if (!url) return;
    setStatus("ingesting");
    setProgress(0);
    setStage("Starting...");
    
    try {
      const res = await fetch(`${API_BASE}/api/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, interval }),
      });
      const data = await res.json();
      setSessionId(data.session_id);
      connectWebSocket(data.session_id);
    } catch (err) {
      setStatus("error");
      setStage("Failed to connect to backend");
    }
  };

  const connectWebSocket = (sid: string) => {
    const ws = new WebSocket(`${WS_BASE}/ws/progress/${sid}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.stage) setStage(data.stage.charAt(0).toUpperCase() + data.stage.slice(1));
      if (data.progress) setProgress(data.progress * 100);
      
      if (data.stage === "complete") {
        setStatus("ready");
        ws.close();
      } else if (data.stage === "error") {
        setStatus("error");
        setStage(data.message || "An error occurred during ingestion");
        ws.close();
      }
    };

    ws.onerror = () => {
      setStatus("error");
      setStage("WebSocket connection failed");
    };
  };

  const askQuestion = async () => {
    if (!input || !sessionId || isAsking) return;
    
    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsAsking(true);

    try {
      const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      });
      const data = await res.json();
      
      const aiMsg: Message = { 
        role: "assistant", 
        content: data.answer, 
        sources: data.sources 
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I encountered an error answering that." }]);
    } finally {
      setIsAsking(false);
    }
  };

  const reset = () => {
    setSessionId(null);
    setStatus("idle");
    setProgress(0);
    setStage("");
    setMessages([]);
    setUrl("");
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-slate-50 p-4 md:p-8 font-sans">
      <div className="w-full max-w-4xl">
        <header className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Video className="text-white w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">VidRAG <span className="text-indigo-600 italic">SaaS</span></h1>
          </div>
          {status !== "idle" && (
            <Button variant="ghost" size="sm" onClick={reset} className="text-slate-500 hover:text-indigo-600 transition-colors">
              <RefreshCw className="w-4 h-4 mr-2" /> New Session
            </Button>
          )}
        </header>

        {status === "idle" && (
          <Card className="border-none shadow-xl bg-white/80 backdrop-blur-sm">
            <CardHeader className="text-center space-y-2">
              <CardTitle className="text-3xl font-extrabold text-slate-900">Understand any video visually.</CardTitle>
              <CardDescription className="text-lg text-slate-600">
                Paste a YouTube link and ask questions about what's happening on screen.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 pt-4">
              <div className="flex flex-col gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 ml-1">YouTube Video URL</label>
                  <Input 
                    placeholder="https://www.youtube.com/watch?v=..." 
                    value={url} 
                    onChange={(e) => setUrl(e.target.value)}
                    className="h-12 text-lg rounded-xl border-slate-200 focus:ring-indigo-500"
                  />
                </div>
                <div className="flex items-center gap-4">
                   <div className="flex-1 space-y-2">
                    <label className="text-sm font-medium text-slate-700 ml-1">Frame Interval (sec)</label>
                    <Input 
                      type="number"
                      value={interval} 
                      onChange={(e) => setIntervalValue(parseInt(e.target.value))}
                      className="h-10 rounded-lg border-slate-200"
                    />
                  </div>
                  <div className="flex-1 flex flex-col justify-end">
                    <Button 
                      onClick={startIngestion} 
                      className="h-12 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-indigo-200 transition-all active:scale-95"
                    >
                      Process Video
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="bg-slate-50/50 rounded-b-xl border-t border-slate-100 p-6 flex justify-around text-slate-500 text-sm">
               <div className="flex items-center gap-2"><ImageIcon className="w-4 h-4" /> Visual Analysis</div>
               <div className="flex items-center gap-2"><MessageSquare className="w-4 h-4" /> Semantic Q&A</div>
               <div className="flex items-center gap-2"><ExternalLink className="w-4 h-4" /> Frame Sources</div>
            </CardFooter>
          </Card>
        )}

        {(status === "ingesting" || status === "error") && (
          <Card className="border-none shadow-xl overflow-hidden">
             <div className="h-2 bg-slate-100">
                <div 
                  className={`h-full transition-all duration-500 ${status === "error" ? "bg-red-500" : "bg-indigo-600"}`}
                  style={{ width: `${progress}%` }}
                />
             </div>
            <CardHeader className="text-center py-12">
              <div className="mx-auto bg-indigo-50 w-20 h-20 rounded-full flex items-center justify-center mb-6">
                {status === "error" ? (
                  <div className="text-red-500 text-4xl">!</div>
                ) : (
                  <Loader2 className="w-10 h-10 text-indigo-600 animate-spin" />
                )}
              </div>
              <CardTitle className={`text-2xl ${status === "error" ? "text-red-600" : "text-slate-900"}`}>
                {status === "error" ? "Ingestion Failed" : "Processing Video..."}
              </CardTitle>
              <CardDescription className="text-slate-500 mt-2 max-w-md mx-auto">
                {stage || "Analyzing video content and extracting key frames..."}
              </CardDescription>
            </CardHeader>
            {status === "error" && (
              <CardFooter className="justify-center pb-12">
                <Button onClick={reset} variant="outline" className="rounded-xl px-8 border-slate-200">
                  Try Again
                </Button>
              </CardFooter>
            )}
          </Card>
        )}

        {status === "ready" && (
          <div className="flex flex-col h-[80vh] bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-100">
            <div className="bg-white border-b border-slate-100 p-4 flex items-center justify-between">
               <div className="flex items-center gap-3">
                  <Badge variant="secondary" className="bg-indigo-50 text-indigo-700 hover:bg-indigo-50 border-none px-3 py-1">Active Session</Badge>
                  <span className="text-sm text-slate-400 truncate max-w-xs">{url}</span>
               </div>
            </div>

            <ScrollArea className="flex-1 p-6">
              <div className="space-y-8">
                {messages.length === 0 && (
                  <div className="text-center py-20 opacity-40">
                    <MessageSquare className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                    <p className="text-xl font-medium text-slate-400">Video is ready. Ask your first question!</p>
                  </div>
                )}
                {messages.map((m, i) => (
                  <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[85%] rounded-2xl p-4 shadow-sm ${
                      m.role === "user" 
                        ? "bg-indigo-600 text-white rounded-tr-none" 
                        : "bg-slate-50 text-slate-800 border border-slate-100 rounded-tl-none"
                    }`}>
                      <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p>
                      
                      {m.sources && m.sources.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-slate-200/50">
                           <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Sources (Click to view)</p>
                           <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
                              {m.sources.map((src, j) => (
                                <a 
                                  key={j} 
                                  href={`${API_BASE}${src.frame_url}`} 
                                  target="_blank" 
                                  rel="noreferrer"
                                  className="group relative flex-shrink-0"
                                >
                                  <div className="w-32 h-20 rounded-lg overflow-hidden border border-slate-200 transition-all group-hover:border-indigo-400 group-hover:shadow-md">
                                     <img 
                                        src={`${API_BASE}${src.frame_url}`} 
                                        alt={`Frame at ${src.timestamp}`} 
                                        className="w-full h-full object-cover transition-transform group-hover:scale-110"
                                     />
                                     <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                        <ExternalLink className="text-white w-4 h-4" />
                                     </div>
                                  </div>
                                  <span className="text-[10px] font-mono mt-1 block text-slate-500 text-center">{src.timestamp}</span>
                                </a>
                              ))}
                           </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {isAsking && (
                  <div className="flex justify-start">
                    <div className="bg-slate-50 border border-slate-100 rounded-2xl rounded-tl-none p-4 shadow-sm">
                       <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
                    </div>
                  </div>
                )}
                <div ref={scrollRef} />
              </div>
            </ScrollArea>

            <div className="p-4 bg-slate-50/50 border-t border-slate-100">
               <div className="relative flex items-center max-w-3xl mx-auto">
                  <Input 
                    placeholder="Ask about the video..." 
                    value={input} 
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && askQuestion()}
                    disabled={isAsking}
                    className="pr-12 h-14 bg-white border-slate-200 rounded-2xl shadow-sm focus:ring-2 focus:ring-indigo-500/20"
                  />
                  <Button 
                    size="icon"
                    onClick={askQuestion} 
                    disabled={isAsking || !input}
                    className="absolute right-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl w-10 h-10 transition-all active:scale-90"
                  >
                    <Send className="w-5 h-5" />
                  </Button>
               </div>
               <p className="text-[10px] text-center text-slate-400 mt-2">VidRAG can make mistakes. Verify important info.</p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
