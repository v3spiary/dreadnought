<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { TrendingUp, TrendingDown, BarChart3, Apple, Bike, ListChecks, Target } from 'lucide-vue-next';
import { api } from '@/lib/api'

const router = useRouter()
const input = ref('')
const sending = ref(false)

</script>

<template>
  <div>
    <h3 class="uk-margin-middle-bottom">Personal Tracker Dashboards</h3>
  </div>

  <div class="uk-child-width-1-1@s" uk-grid>
    <div>
        <div uk-grid>
            <div class="uk-width-auto@m">
                <ul class="uk-tab-left" uk-tab="connect: #component-tab-left; animation: uk-animation-fade">
                    <li><a href="#"><BarChart3 :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Базовые</a></li>
                    <li><a href="#"><Apple :size="15" stroke-width="1.3"style="padding-right: 3px;" /> Питание</a></li>
                    <li><a href="#"><Bike :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Спорт</a></li>
                    <li><a href="#"><ListChecks :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Дисциплина</a></li>
                    <li><a href="#"><Target :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Саморазвитие</a></li>
                </ul>
            </div>
            <div class="uk-width-expand@m">
                <div id="component-tab-left" class="uk-switcher">

                    <div>

                      <div class="uk-alert-primary" uk-alert>
                          <a class="uk-alert-close" uk-close></a>
                          <p><span uk-icon="icon: warning;" style="padding-right: 5px;"></span> Действующий форс-мажор: Восстановление после операции.</p>
                      </div>

                      <div class="uk-slider-container-offset" uk-slider>
                        <div class="uk-position-relative uk-visible-toggle" tabindex="-1">
                          <div class="uk-slider-items uk-child-width-1-1@s uk-grid">

                            <div>

                                      <div class="uk-grid-small uk-child-width-1-6@s uk-text-center"  uk-grid uk-height-match="target: > div > .uk-card">
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body ">
                                                <h1 class="uk-text-success uk-margin-small-top">A-</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Оценка дня</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">ккал</div>
                                                <h1 class="uk-text-warning uk-margin-small-top">2150</h1>
                                                <p><TrendingDown class="uk-text-danger"/></p>
                                                <p class="uk-text-muted">Калории</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">шагов</div>
                                                <h1 class="uk-text-success uk-margin-small-top">23781</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Пройдено за сегодня</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">ч</div>
                                                <h1 class="uk-text-danger uk-margin-small-top">4</h1>
                                                <p><TrendingDown class="uk-text-danger"/></p>
                                                <p class="uk-text-muted">Сон</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">л</div>
                                                <h1 class="uk-text-success uk-margin-small-top">4.2</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Вода</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">страниц</div>
                                                <h1 class="uk-text-success uk-margin-small-top">32</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Прочитано</p>
                                              </div>
                                          </div>
                                        
                                      </div>

                                      <div class="uk-grid-small uk-child-width-1-2@s uk-text-center"  uk-grid uk-height-match="target: > div > .uk-card">
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body ">
                                                <h1 class="uk-text-success uk-margin-small-top">A-</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Оценка дня</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">ккал</div>
                                                <h1 class="uk-text-warning uk-margin-small-top">2150</h1>
                                                <p><TrendingDown class="uk-text-danger"/></p>
                                                <p class="uk-text-muted">Калории</p>
                                              </div>
                                          </div>
                                        
                                      </div>

                            </div>
                            <div>

                                      <div class="uk-grid-small uk-child-width-1-6@s uk-text-center"  uk-grid uk-height-match="target: > div > .uk-card">
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body ">
                                                <h1 class="uk-text-success uk-margin-small-top">A-</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Оценка дня</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">ккал</div>
                                                <h1 class="uk-text-warning uk-margin-small-top">2150</h1>
                                                <p><TrendingDown class="uk-text-danger"/></p>
                                                <p class="uk-text-muted">Калории</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">шагов</div>
                                                <h1 class="uk-text-success uk-margin-small-top">23781</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Пройдено за сегодня</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">ч</div>
                                                <h1 class="uk-text-danger uk-margin-small-top">4</h1>
                                                <p><TrendingDown class="uk-text-danger"/></p>
                                                <p class="uk-text-muted">Сон</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">л</div>
                                                <h1 class="uk-text-success uk-margin-small-top">4.2</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Вода</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">страниц</div>
                                                <h1 class="uk-text-success uk-margin-small-top">32</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Прочитано</p>
                                              </div>
                                          </div>
                                        
                                      </div>

                                      <div class="uk-grid-small uk-child-width-1-2@s uk-text-center"  uk-grid uk-height-match="target: > div > .uk-card">
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body ">
                                                <h1 class="uk-text-success uk-margin-small-top">A-</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Оценка дня</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">ккал</div>
                                                <h1 class="uk-text-warning uk-margin-small-top">2150</h1>
                                                <p><TrendingDown class="uk-text-danger"/></p>
                                                <p class="uk-text-muted">Калории</p>
                                              </div>
                                          </div>
                                        
                                      </div>

                            </div>
                            <div>

                                      <div class="uk-grid-small uk-child-width-1-6@s uk-text-center"  uk-grid uk-height-match="target: > div > .uk-card">
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body ">
                                                <h1 class="uk-text-success uk-margin-small-top">A-</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Оценка дня</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">ккал</div>
                                                <h1 class="uk-text-warning uk-margin-small-top">2150</h1>
                                                <p><TrendingDown class="uk-text-danger"/></p>
                                                <p class="uk-text-muted">Калории</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">шагов</div>
                                                <h1 class="uk-text-success uk-margin-small-top">23781</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Пройдено за сегодня</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">ч</div>
                                                <h1 class="uk-text-danger uk-margin-small-top">4</h1>
                                                <p><TrendingDown class="uk-text-danger"/></p>
                                                <p class="uk-text-muted">Сон</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">л</div>
                                                <h1 class="uk-text-success uk-margin-small-top">4.2</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Вода</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">страниц</div>
                                                <h1 class="uk-text-success uk-margin-small-top">32</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Прочитано</p>
                                              </div>
                                          </div>
                                        
                                      </div>

                                      <div class="uk-grid-small uk-child-width-1-2@s uk-text-center"  uk-grid uk-height-match="target: > div > .uk-card">
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body ">
                                                <h1 class="uk-text-success uk-margin-small-top">A-</h1>
                                                <p><TrendingUp class="uk-text-success"/></p>
                                                <p class="uk-text-muted">Оценка дня</p>
                                              </div>
                                          </div>
                                          <div>
                                              <div class="uk-card uk-card-default uk-card-body">
                                                <div class="uk-card-badge uk-label">ккал</div>
                                                <h1 class="uk-text-warning uk-margin-small-top">2150</h1>
                                                <p><TrendingDown class="uk-text-danger"/></p>
                                                <p class="uk-text-muted">Калории</p>
                                              </div>
                                          </div>
                                        
                                      </div>

                            </div>
                        
                          </div>
                          <a class="uk-position-center-left uk-position-small uk-hidden-hover uk-dark" uk-slidenav-previous uk-slider-item="previous"></a>
                          <a class="uk-position-center-right uk-position-small uk-hidden-hover uk-dark" uk-slidenav-next uk-slider-item="next"></a>
                        </div>
                        <ul class="uk-slider-nav uk-dotnav uk-flex-center uk-position-bottom-center uk-margin"></ul>
                      </div>

                      

                    </div>

                    <div>

                      <div class="uk-grid-medium uk-child-width-expand@s uk-text-center" uk-grid>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">
                              2
                            </div>
                        </div>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">Item</div>
                        </div>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">Item</div>
                        </div>
                      </div>

                    </div>

                    <div>

                      <div class="uk-grid-medium uk-child-width-expand@s uk-text-center" uk-grid>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">
                              3
                            </div>
                        </div>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">Item</div>
                        </div>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">Item</div>
                        </div>
                      </div>

                    </div>

                    <div>

                      <div class="uk-grid-medium uk-child-width-expand@s uk-text-center" uk-grid>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">
                              4
                            </div>
                        </div>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">Item</div>
                        </div>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">Item</div>
                        </div>
                      </div>

                    </div>

                    <div>

                      <div class="uk-grid-medium uk-child-width-expand@s uk-text-center" uk-grid>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">
                              5
                            </div>
                        </div>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">Item</div>
                        </div>
                        <div>
                            <div class="uk-card uk-card-default uk-card-body">Item</div>
                        </div>
                      </div>

                    </div>

                </div>
            </div>
        </div>
    </div>
  </div>
</template>
