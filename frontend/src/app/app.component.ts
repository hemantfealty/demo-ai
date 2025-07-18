import { Component } from '@angular/core';
import { InterfaceComponent } from './components/interface/interface.component';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [ InterfaceComponent ], 
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss'
})
export class AppComponent {
}