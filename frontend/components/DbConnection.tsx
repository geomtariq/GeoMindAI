'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from './ui/Card';
import { Input } from './ui/Input';
import { Button } from './ui/Button';
import { Database, Server, User, Key, Globe, Activity } from 'lucide-react';

interface DbConnectionProps {
  onConnect: (connectionDetails: any) => Promise<void>;
  isConnected: boolean;
  sessionId?: string;
}

export default function DbConnection({ onConnect, isConnected, sessionId }: DbConnectionProps) {
  const [host, setHost] = useState('');
  const [port, setPort] = useState(1521);
  const [serviceName, setServiceName] = useState('');
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleConnect = async () => {
    setIsLoading(true);
    setError('');
    try {
      await onConnect({ host, port, service_name: serviceName, user, password });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (isConnected) {
    return null;
  }

  return (
    <div className="flex items-center justify-center p-4 animate-in fade-in zoom-in duration-500">
      <Card className="w-full max-w-md border-primary/20 shadow-2xl shadow-primary/10 bg-card/80 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-2xl text-primary">
            <Database className="w-6 h-6" />
            Connect to Database
          </CardTitle>
          <CardDescription>
            Enter your Oracle database credentials to start analyzing.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2 col-span-2">
              <div className="relative">
                <Globe className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Host"
                  value={host}
                  onChange={(e) => setHost(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
            <div className="space-y-2">
              <div className="relative">
                <Activity className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="number"
                  placeholder="Port"
                  value={port}
                  onChange={(e) => setPort(parseInt(e.target.value))}
                  className="pl-9"
                />
              </div>
            </div>
            <div className="space-y-2">
              <div className="relative">
                <Server className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Service Name"
                  value={serviceName}
                  onChange={(e) => setServiceName(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
            <div className="space-y-2 col-span-2">
              <div className="relative">
                <User className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="User"
                  value={user}
                  onChange={(e) => setUser(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
            <div className="space-y-2 col-span-2">
              <div className="relative">
                <Key className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
          </div>
          {error && <p className="text-sm text-destructive font-medium text-center">{error}</p>}
        </CardContent>
        <CardFooter>
          <Button
            onClick={handleConnect}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/20"
            disabled={isLoading}
          >
            {isLoading ? "Connecting..." : "Connect"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
