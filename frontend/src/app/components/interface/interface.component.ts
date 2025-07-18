import { Component } from '@angular/core';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { ChatComponent } from '../chat/chat.component';
import { ChatService } from '../../services/chat.service';

@Component({
  selector: 'app-interface',
  standalone: true,
  imports: [ SidebarComponent, ChatComponent ], 
  templateUrl: './interface.component.html',
  styleUrl: './interface.component.scss'
})
export class InterfaceComponent {
  isCollapsed = false;
  currentChatId: string | null = null;
  sidebarRefreshFlag = false;
  latestChatTitle: {title: string, chatId: string} = {title: '', chatId: ''};
  // Track if current chat is empty to prevent consecutive new chats
  isCurrentChatEmpty = true;

  constructor(private chatService: ChatService) {
    this.geterrorMessage();
  }

  onChatIdChange(chatId: string | null) {
    this.currentChatId = chatId;
    // When switching to an existing chat, we need to check if it's empty
    // This will be handled by the chat component when it loads the messages
  }

  onToggle(isCollapsed: boolean) {
    this.isCollapsed = isCollapsed;
  }

  // Handle new chat creation from sidebar
  onNewChatRequest() {
    // Only create new chat if current chat is not empty
    if (this.isCurrentChatEmpty || this.latestChatTitle.title == 'New Chat') {
      console.log('Latest chat title is: ' + this.latestChatTitle);
      console.log('Current chat is empty, not creating new chat');
      if (this.latestChatTitle.title == 'New Chat') {
        // set chatid to the latest chat id
        this.currentChatId = this.latestChatTitle.chatId;
      }
      return;
    }

    this.chatService.newChatId().subscribe({
      next: (response: any) => {
        this.currentChatId = response.data.id;
        this.isCurrentChatEmpty = true; // New chat starts empty
        this.sidebarRefreshFlag = !this.sidebarRefreshFlag; // Trigger sidebar refresh
      },
      error: (err: any) => {
        console.error('Error creating new chat:', err);
      }
    });
  }

  // Called when chat component indicates chat is no longer empty
  onChatNotEmpty() {
    this.isCurrentChatEmpty = false;
  }

  // Called when chat component indicates chat is empty
  onChatEmpty() {
    this.isCurrentChatEmpty = true;
  }

  geterrorMessage() {
    // this.http.getErrorLoadedMessageStatus().subscribe({
    //   next: (value) => {
    //     if (value.status == '401') {
    //       console.log('401 error');
    //     }
    //   },
    // });
  }

  // Called when ChatComponent wants to reload the sidebar
  handleFetchChatsRequest() {
    this.sidebarRefreshFlag = !this.sidebarRefreshFlag;
  }

  onLatestChatTitle(data: {title: string, chatId: string}) {
    this.latestChatTitle = data;
  }
}
