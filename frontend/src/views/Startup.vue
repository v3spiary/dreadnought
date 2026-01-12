<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/lib/api'

const router = useRouter()
const input = ref('')
const sending = ref(false)

</script>

<template>
    <!-- Модалка -->
    <div id="modal-startup-detail" class="uk-modal-container" uk-modal>
        <div class="uk-modal-dialog uk-modal-body">
            <div class="uk-container">
                <button class="uk-modal-close-default" type="button" uk-close></button>
                                    
                <article class="uk-article uk-margin-bottom">

                    <h3 class="uk-article-title">Название проекта</h3>

                    <p class="uk-article-meta">Written by <a href="#">Super User</a> on 12 April 2012. Posted in <a href="#">Blog</a></p>

                    <p class="uk-text-lead">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip.</p>

                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>

                </article>
            </div>
        </div>
    </div>

    <div uk-filter="target: .js-filter">
        <h3 class="uk-margin-middle-bottom">Startup Platform</h3>

        <div class="uk-grid-small uk-flex-middle" uk-grid>
            <div class="uk-width-expand">

                <div class="uk-grid-small uk-grid-divider uk-child-width-auto" uk-grid>
                    <div>
                        <ul class="uk-subnav uk-subnav-pill" uk-margin>
                            <li class="uk-active" uk-filter-control><a href="#">All</a></li>
                        </ul>
                    </div>
                    <div>
                        <ul class="uk-subnav uk-subnav-pill" uk-margin>
                            <li uk-filter-control="[data-color='white']"><a href="#">White</a></li>
                            <li uk-filter-control="[data-color='blue']"><a href="#">Blue</a></li>
                            <li uk-filter-control="[data-color='black']"><a href="#">Black</a></li>
                        </ul>
                    </div>
                </div>

            </div>
            <div class="uk-width-auto uk-text-nowrap">


                <span class="uk-active" uk-filter-control="sort: data-date"><a class="uk-icon-link" href="#" uk-icon="icon: arrow-down" aria-label="Sort ascending"></a></span>
                <span uk-filter-control="sort: data-date; order: desc"><a class="uk-icon-link" href="#" uk-icon="icon: arrow-up" aria-label="Sort descending"></a></span>

            </div>
        </div>

        <div class="uk-child-width-1-4@m uk-grid-small" uk-grid="masonry: pack">

            <ul uk-sortable="group: sortable-group" class="js-filter" style="list-style-type: none; padding-left: 0;">
                <li data-color="white" data-date="2016-03-01">
                    <div>
                        <div class="uk-card uk-card-default uk-card-hover">
                            <div class="uk-card-body">
                                <div class="uk-card-badge uk-label uk-label-success">B2B</div>
                                <h3 class="uk-card-title">Название проекта</h3>

                                <ul class="uk-subnav uk-subnav-pill" uk-switcher>
                                    <li><a href="#">Идея</a></li>
                                    <li><a href="#">ЦА</a></li>
                                    <li><a href="#">Показатели</a></li>
                                </ul>

                                <div class="uk-switcher uk-margin">

                                    <div>
                                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                                    </div>

                                    <div>


                                            <div>
                                                <div uk-grid>
                                                    <div class="uk-width-auto@m uk-flex-last@m">
                                                        <ul class="uk-tab-right" uk-tab="connect: #component-tab-right; animation: uk-animation-fade">
                                                            <li><a href="#">WHAT</a></li>
                                                            <li><a href="#">WHO</a></li>
                                                            <li><a href="#">WHY</a></li>
                                                            <li><a href="#">WHEN</a></li>
                                                            <li><a href="#">WHERE</a></li>
                                                        </ul>
                                                    </div>
                                                    <div class="uk-width-expand@m">
                                                        <div id="component-tab-right" class="uk-switcher">

                                                            <div>
                                                                <p>Что продаем?</p>
                                                            </div>

                                                            <div>
                                                                <p>Кто купит?</p>
                                                            </div>

                                                            <div>
                                                                <p>Зачем это ему?</p>
                                                            </div>

                                                            <div>
                                                                <p>Когда купит?</p>
                                                            </div>

                                                            <div>
                                                                <p>Где купит?</p>
                                                            </div>

                                                        </div>
                                                    </div>
                                                </div>
                                            </div>


                                    </div>

                                    <div>
                                    <div class="uk-grid-small" uk-grid>
                                        <div class="uk-width-expand" uk-leader>NPV</div>
                                        <div class="uk-text-success">2.000.000</div>
                                    </div>
                                    <div class="uk-grid-small" uk-grid>
                                        <div class="uk-width-expand" uk-leader>FPV</div>
                                        <div class="uk-text-success">1,5 года</div>
                                    </div>
                                    <div class="uk-grid-small" uk-grid>
                                        <div class="uk-width-expand" uk-leader>FSB</div>
                                        <div class="uk-text-warning">32%</div>
                                    </div>
                                    <div class="uk-grid-small" uk-grid>
                                        <div class="uk-width-expand" uk-leader>ABC</div>
                                        <div class="uk-text-danger">4.2</div>
                                    </div>
                                    <div class="uk-grid-small" uk-grid>
                                        <div class="uk-width-expand" uk-leader>ETC</div>
                                        <div class="uk-text-warning">1</div>
                                    </div>
                                    </div>

                                </div>

                            </div>
                            <div class="uk-card-footer">
                                <a href="#modal-startup-detail" class="uk-button uk-button-text" uk-toggle>Открыть</a>
                            </div>
                        </div>
                    </div>
                </li>
            </ul>

        </div>

    </div>
</template>
