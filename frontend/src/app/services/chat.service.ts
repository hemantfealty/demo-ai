import { Injectable, } from '@angular/core';
import { Observable, } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';  

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  constructor( private http: HttpClient) {}

  sendMessage(message: string, chatid: string| null): Observable<any> {
    const payload = {
      human_message: message
    };
    return this.http.post( 
      `chat-sessions/${chatid}/messages`,
      payload
    )
  }
  previousMessage(chatid: string | null): Observable<any> {
      return this.http.get(
        `chat-sessions/${chatid}`,
        );
  }
  newChatId(): Observable<any> {
    const payload = {
      title: 'New Chat',
    };
    return this.http.post(
      'chat-sessions/',
      payload
    )
  }

    getChatIds(): Observable<any> {
      return this.http.get(
        'chat-sessions/user/me',
        );

  }
}