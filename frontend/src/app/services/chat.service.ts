import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from '../environments/environment'; // adjust path if needed

const API_URL = environment.API_URL;

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  constructor(private http: HttpClient) {}

  sendMessage(message: string, chatid: string | null): Observable<any> {
    const payload = { human_message: message };
    return this.http.post(`${API_URL}/chat-sessions/${chatid}/messages`, payload);
  }

  previousMessage(chatid: string | null): Observable<any> {
    return this.http.get(`${API_URL}/chat-sessions/${chatid}`);
  }

  newChatId(): Observable<any> {
    const payload = { title: 'New Chat' };
    return this.http.post(`${API_URL}/chat-sessions/`, payload);
  }

  getChatIds(): Observable<any> {
    return this.http.get(`${API_URL}/chats`);
  }
}
