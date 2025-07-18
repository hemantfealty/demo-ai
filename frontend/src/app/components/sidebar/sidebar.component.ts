import { CommonModule } from '@angular/common';
import {
  Component,
  EventEmitter,
  Input,
  Output,
  OnInit,
  OnChanges,
  SimpleChanges,

} from '@angular/core';
import { ChatService } from '../../services/chat.service';
 
interface ChatSession {
  id: string;
  title: string;
  updated_at: string;
}
 
@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent implements OnInit, OnChanges {
  @Input() isCollapsed = false;
  @Input() currentChatId: string | null = null;
  @Input() refreshTrigger: boolean = false;
  
  @Output() startNewChatClicked = new EventEmitter<void>();
  @Output() toggleEvent = new EventEmitter<boolean>();
  @Output() portalSwitch = new EventEmitter<string>();
  @Output() chatIdChange = new EventEmitter<string>();
  // Latest chat title
  @Output() latestChatTitle = new EventEmitter<{title: string, chatId: string}>();


  chatSessions: { chatId: string; preview: string; timestamp: string }[] = [];
 
  constructor(private chatService: ChatService) {}

  ngOnInit() {
    this.fetchChats();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['refreshTrigger'] && !changes['refreshTrigger'].firstChange) {
      this.fetchChats();
    }
  }

  fetchChats() {
    this.chatService.getChatIds()
      .subscribe((res: any) => {
        if (!res.status || !Array.isArray(res.data)) return;
 
        this.chatSessions = res.data.map((c: ChatSession) => ({
          chatId: c.id,
          preview: c.title,
          timestamp: new Date(c.updated_at)
                      .toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }));
      }, err => console.error('fetchChats error', err));
  }

  switchChat(chatId: string) {
    this.chatIdChange.emit(chatId);
    this.getLatestChatTitle();
  }

  getLatestChatTitle() {
    this.latestChatTitle.emit({title: this.chatSessions[0].preview, chatId: this.chatSessions[0].chatId});
  }
 
  selectPortal(portal: string) {
    this.portalSwitch.emit(portal);
  }
 
  toggleSidebar() {
    this.isCollapsed = !this.isCollapsed;
    this.toggleEvent.emit(this.isCollapsed);
  }

  backToWebsite() {
    window.location.href = 'https://fealtytechnologies.com/';
  }
}
