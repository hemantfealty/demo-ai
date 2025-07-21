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
    const payload = { question: message };
    return this.http.post(`${API_URL}/chats/${chatid}/messages`, payload);
  }

  previousMessage(chatid: string | null): Observable<any> {
    return this.http.get(`${API_URL}/chats/${chatid}/messages`);
  }

  newChatId(): Observable<any> {
    return this.http.get(`${API_URL}/chats/`);
  }

  getChatIds(): Observable<any> {
    return this.http.get(`${API_URL}/chats`);
  }
}
